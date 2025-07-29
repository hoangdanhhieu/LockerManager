/*
 * locker_func.h
 *
 *  Created on: Jun 2, 2025
 *      Author: nonamezz
 */

#include "locker_func.h"
#include "main.h"
#include "command_rev.h"

uint32_t channel_status = 0;

void send_data(uint8_t *data, uint8_t size) {
	HAL_GPIO_WritePin(GPIOA, REDE_Pin, GPIO_PIN_SET);
	HAL_UART_Transmit(&huart1, data, size, 100);
	HAL_GPIO_WritePin(GPIOA, REDE_Pin, GPIO_PIN_RESET);
}

uint8_t checksum(uint8_t *data, uint8_t size) {
	uint8_t xor = data[0];
	for (int i = 1; i < size; i++) {
		xor ^= data[i];
	}
	return xor;
}

void broadcast_func() {
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = BROADCAST_ADDRESS;
	tx_buff[3] = BOARDCAST_CODE;
	tx_buff[4] = 1;
	tx_buff[5] = ADDRESS;
	tx_buff[6] = checksum(tx_buff, 6);
	send_data(tx_buff, 7);
}

void getMCUID_func() {
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = ADDRESS;
	tx_buff[3] = READ_MCU_ID_CODE;
	tx_buff[4] = 7;
	for (int i = 0; i < 7; i++) {
		tx_buff[i + 5] = (CPU_ID >> (8 * (6 - i))) & 0xFF;
	}
	tx_buff[12] = checksum(tx_buff, 12);
	send_data(tx_buff, 13);
}

void writeChannel_func() {
	writePin(rx_buff[5], rx_buff[6]);
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = ADDRESS;
	tx_buff[3] = WRITE_CHANNEL_CODE;
	tx_buff[4] = 2;
	tx_buff[5] = rx_buff[5];
	tx_buff[6] = rx_buff[6];
	tx_buff[7] = checksum(tx_buff, 7);
	send_data(tx_buff, 8);
}

void readConfig_func() {
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = ADDRESS;
	tx_buff[3] = READ_CONFIG_CODE;
	tx_buff[4] = 5;
	tx_buff[5] = (BAUD_RATE >> 24) & 0xFF;
	tx_buff[6] = (BAUD_RATE >> 16) & 0xFF;
	tx_buff[7] = (BAUD_RATE >> 8) & 0xFF;
	tx_buff[8] = (BAUD_RATE >> 0) & 0xFF;
	tx_buff[9] = UNLOCK_TIME;
	tx_buff[10] = checksum(tx_buff, 10);
	send_data(tx_buff, 11);
}

void writeConfig_func() {
	BAUD_RATE = ((uint32_t) rx_buff[5] << 24) | ((uint32_t) rx_buff[6] << 16)
			| ((uint32_t) rx_buff[7] << 8) | ((uint32_t) rx_buff[8] << 0);
	UNLOCK_TIME = rx_buff[9];
	readConfig_func();
	HAL_UART_Abort_IT(&huart1);
	HAL_UART_DeInit(&huart1);
	huart1.Init.BaudRate = BAUD_RATE;
	if (HAL_UART_Init(&huart1) != HAL_OK) {
		// Initialization Error
		Error_Handler();
	}
	if (HAL_UARTEx_ReceiveToIdle_IT(&huart1, rx_buff, 30) != HAL_OK) {
		// Reception Error
		Error_Handler();
	}
}

void readChannelStatus_func() {
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = ADDRESS;
	tx_buff[3] = READ_CHANNEL_STATUS_CODE;
	if (rx_buff[5] == 0) {
		tx_buff[4] = 4;
		tx_buff[5] = (channel_status >> 24) & 0xFF;
		tx_buff[6] = (channel_status >> 16) & 0xFF;
		tx_buff[7] = (channel_status >> 8) & 0xFF;
		tx_buff[8] = (channel_status >> 8) & 0xFF;
		tx_buff[9] = checksum(tx_buff, 9);
		send_data(tx_buff, 10);
	} else {
		tx_buff[4] = 1;
		tx_buff[5] =
				channel_status & ((uint32_t) 1 << (31 - rx_buff[5])) ? 1 : 0;
		tx_buff[6] = checksum(tx_buff, 6);
		send_data(tx_buff, 7);
	}
}

void readChannelSignalStatus_func() {
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = ADDRESS;
	tx_buff[3] = READ_CHANNEL_SIGNAL_STATUS_CODE;
	uint32_t channel_signal_status = 0;
	for (int i = 1; i <= MAX_CHANNEL; i++) {
		write_bit_to_num(&channel_signal_status, i, readPin(i));
	}
	if (rx_buff[5] == 0) {
		tx_buff[4] = 4;
		tx_buff[5] = (channel_signal_status >> 24) & 0xFF;
		tx_buff[6] = (channel_signal_status >> 16) & 0xFF;
		tx_buff[7] = (channel_signal_status >> 8) & 0xFF;
		tx_buff[8] = (channel_signal_status >> 8) & 0xFF;
		tx_buff[9] = checksum(tx_buff, 9);
		send_data(tx_buff, 10);
	} else {
		tx_buff[4] = 1;
		tx_buff[5] =
				channel_signal_status & ((uint32_t) 1 << (31 - rx_buff[5])) ?
						1 : 0;
		tx_buff[6] = checksum(tx_buff, 6);
		send_data(tx_buff, 7);
	}
}

void unlock_func() {
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = ADDRESS;
	tx_buff[3] = UNLOCK_CODE;
	tx_buff[4] = 0x02;
	tx_buff[5] = rx_buff[5];
	tx_buff[6] = 0x01;
	tx_buff[7] = checksum(tx_buff, 7);
	if (rx_buff[5] == 0) {
		for (uint8_t i = 1; i <= MAX_CHANNEL; i++) {
			writePin(i, 1);
			HAL_Delay((uint32_t) UNLOCK_TIME * 10);
			writePin(i, 0);
		}
	} else {
		writePin(rx_buff[5], 1);
		HAL_Delay((uint32_t) UNLOCK_TIME * 10);
		writePin(rx_buff[5], 0);
	}
	send_data(tx_buff, 8);
}

void rusc1_func() {
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = ADDRESS;
	tx_buff[3] = RUSC1_CODE;
	tx_buff[4] = 0x02;
	tx_buff[5] = rx_buff[5];
	uint32_t start_time = HAL_GetTick();
	uint32_t overtime = rx_buff[6] * 100;
	uint8_t last_status = readPin(rx_buff[5]);
	writePin(rx_buff[5], 1);
	while (1) {
		uint8_t status = readPin(rx_buff[5]);
		if (HAL_GetTick() - start_time > overtime) {
			tx_buff[6] = 0x03;
			break;
		} else if (last_status != status && status == rx_buff[7]) {
			tx_buff[6] = 0x01;
			break;
		} else {
			last_status = status;
		}
	}
	writePin(rx_buff[5], 0);
	tx_buff[7] = checksum(tx_buff, 7);
	send_data(tx_buff, 8);
}

void rusc2_func() {
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = ADDRESS;
	tx_buff[3] = RUSC2_CODE;
	tx_buff[4] = 0x02;
	tx_buff[5] = rx_buff[5];
	uint32_t start_time = HAL_GetTick();
	uint32_t overtime = rx_buff[6] * 100;
	uint8_t last_status = readPin(rx_buff[5]);
	uint8_t count_changes = 0;
	writePin(rx_buff[5], 1);
	while (1) {
		uint8_t status = readPin(rx_buff[5]);
		if (HAL_GetTick() - start_time > overtime) {
			tx_buff[6] = 0x03;
			break;
		} else if (count_changes >= rx_buff[7]) {
			tx_buff[6] = 0x01;
			break;
		} else {
			if (last_status != status) {
				last_status = status;
				count_changes += 1;
			}
		}
	}
	writePin(rx_buff[5], 0);
	tx_buff[7] = checksum(tx_buff, 7);
	send_data(tx_buff, 8);
}

void rusc3_func() {
	tx_buff[0] = HEADER;
	tx_buff[1] = TYPE_CODE;
	tx_buff[2] = ADDRESS;
	tx_buff[3] = RUSC3_CODE;
	tx_buff[4] = 0x02;
	tx_buff[5] = rx_buff[5];
	uint32_t start_time = HAL_GetTick();
	uint32_t overtime = rx_buff[6] * 100;
	writePin(rx_buff[5], 1);
	while (1) {
		if (HAL_GetTick() - start_time > overtime) {
			tx_buff[6] = 0x03;
			break;
		} else if (rx_buff[7] == readPin(rx_buff[5])) {
			tx_buff[6] = 0x01;
			break;
		}
	}
	writePin(rx_buff[5], 0);
	tx_buff[7] = checksum(tx_buff, 7);
	send_data(tx_buff, 8);
}

void unlock_all() {
	for (int i = 1; i <= MAX_CHANNEL; i++) {
		writePin(i, 1);
		HAL_Delay((uint32_t) UNLOCK_TIME * 10);
		writePin(i, 0);
	}
}

void write_bit_to_num(uint32_t *num, uint8_t index, uint8_t value) {
	index = 31 - index;
	if (value) {
		*num |= ((uint32_t) 1 << index);
	} else {
		*num &= ~((uint32_t) 1 << index);
	}
}

uint8_t readPin(uint8_t PIN) {
	uint8_t res = 0;
	switch (PIN) {
	case 1:
		res = HAL_GPIO_ReadPin(GPIOB, F1_Pin);
		break;
	case 2:
		res = HAL_GPIO_ReadPin(GPIOB, F2_Pin);
		break;
	case 3:
		res = HAL_GPIO_ReadPin(GPIOB, F3_Pin);
		break;
	case 4:
		res = HAL_GPIO_ReadPin(GPIOB, F4_Pin);
		break;
	case 5:
		res = HAL_GPIO_ReadPin(GPIOC, F5_Pin);
		break;
	case 6:
		res = HAL_GPIO_ReadPin(GPIOA, F6_Pin);
		break;
	case 7:
		res = HAL_GPIO_ReadPin(GPIOA, F7_Pin);
		break;
	case 8:
		res = HAL_GPIO_ReadPin(GPIOA, F8_Pin);
		break;
	case 9:
		res = HAL_GPIO_ReadPin(GPIOC, F9_Pin);
		break;
	case 10:
		res = HAL_GPIO_ReadPin(GPIOA, F10_Pin);
		break;
	case 11:
		res = HAL_GPIO_ReadPin(GPIOA, F11_Pin);
		break;
	case 12:
		res = HAL_GPIO_ReadPin(GPIOC, F12_Pin);
		break;
	case 13:
		res = HAL_GPIO_ReadPin(GPIOD, F13_Pin);
		break;
	case 14:
		res = HAL_GPIO_ReadPin(GPIOB, F14_Pin);
		break;
	case 15:
		res = HAL_GPIO_ReadPin(GPIOB, F15_Pin);
		break;
	case 16:
		res = HAL_GPIO_ReadPin(GPIOB, F16_Pin);
		break;
	}
	return res;
}

void writePin(uint8_t PIN, uint8_t value) {
	write_bit_to_num(&channel_status, PIN, value);
	value = 1 - value;
	switch (PIN) {
	case 1:
		HAL_GPIO_WritePin(GPIOB, L1_Pin, value);
		break;
	case 2:
		HAL_GPIO_WritePin(GPIOB, L2_Pin, value);
		break;
	case 3:
		HAL_GPIO_WritePin(GPIOB, L3_Pin, value);
		break;
	case 4:
		HAL_GPIO_WritePin(GPIOB, L4_Pin, value);
		break;
	case 5:
		HAL_GPIO_WritePin(GPIOC, L5_Pin, value);
		break;
	case 6:
		HAL_GPIO_WritePin(GPIOA, L6_Pin, value);
		break;
	case 7:
		HAL_GPIO_WritePin(GPIOA, L7_Pin, value);
		break;
	case 8:
		HAL_GPIO_WritePin(GPIOA, L8_Pin, value);
		break;
	case 9:
		HAL_GPIO_WritePin(GPIOC, L9_Pin, value);
		break;
	case 10:
		HAL_GPIO_WritePin(GPIOA, L10_Pin, value);
		break;
	case 11:
		HAL_GPIO_WritePin(GPIOC, L11_Pin, value);
		break;
	case 12:
		HAL_GPIO_WritePin(GPIOC, L12_Pin, value);
		break;
	case 13:
		HAL_GPIO_WritePin(GPIOB, L13_Pin, value);
		break;
	case 14:
		HAL_GPIO_WritePin(GPIOB, L14_Pin, value);
		break;
	case 15:
		HAL_GPIO_WritePin(GPIOB, L15_Pin, value);
		break;
	case 16:
		HAL_GPIO_WritePin(GPIOB, L16_Pin, value);
		break;
	}
}

void readAddress() {
	uint8_t D1 = 1 - HAL_GPIO_ReadPin(GPIOC, D1_Pin);
	uint8_t D2 = 1 - HAL_GPIO_ReadPin(GPIOC, D2_Pin);
	uint8_t D3 = 1 - HAL_GPIO_ReadPin(GPIOC, D3_Pin);
	uint8_t D4 = 1 - HAL_GPIO_ReadPin(GPIOA, D4_Pin);
	uint8_t D5 = 1 - HAL_GPIO_ReadPin(GPIOA, D5_Pin);
	ADDRESS = 1 + ((D1 << 0) | (D2 << 1) | (D3 << 2) | (D4 << 3) | (D5 << 4));
}

/*
 void flash_init() {
 HAL_FLASH_Unlock(); //unlock the flash
 FlashErase.Sector = FLASH_SECTOR_11;
 FlashErase.NbSectors = 1;
 FlashErase.TypeErase = FLASH_TYPEERASE_SECTORS;
 FlashErase.VoltageRange = VOLTAGE_RANGE_3;
 HAL_FLASH_Lock();
 }*/
