/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.h
  * @brief          : Header for main.c file.
  *                   This file contains the common defines of the application.
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f1xx_hal.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
extern uint8_t rx_buff[30];
extern uint8_t tx_buff[30];
void send_data(uint8_t *data, uint8_t size);
uint8_t checksum(uint8_t* data, uint8_t size);
extern UART_HandleTypeDef huart1;
extern uint8_t func_code;
void MX_USART1_UART_Init(void);
/* USER CODE END Includes */

/* Exported types ------------------------------------------------------------*/
/* USER CODE BEGIN ET */

/* USER CODE END ET */

/* Exported constants --------------------------------------------------------*/
/* USER CODE BEGIN EC */

/* USER CODE END EC */

/* Exported macro ------------------------------------------------------------*/
/* USER CODE BEGIN EM */

/* USER CODE END EM */

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* USER CODE BEGIN EFP */

/* USER CODE END EFP */

/* Private defines -----------------------------------------------------------*/
#define D1_Pin GPIO_PIN_1
#define D1_GPIO_Port GPIOC
#define D2_Pin GPIO_PIN_2
#define D2_GPIO_Port GPIOC
#define D3_Pin GPIO_PIN_3
#define D3_GPIO_Port GPIOC
#define D4_Pin GPIO_PIN_0
#define D4_GPIO_Port GPIOA
#define D5_Pin GPIO_PIN_1
#define D5_GPIO_Port GPIOA
#define F8_Pin GPIO_PIN_2
#define F8_GPIO_Port GPIOA
#define L8_Pin GPIO_PIN_3
#define L8_GPIO_Port GPIOA
#define F7_Pin GPIO_PIN_4
#define F7_GPIO_Port GPIOA
#define L7_Pin GPIO_PIN_5
#define L7_GPIO_Port GPIOA
#define F6_Pin GPIO_PIN_6
#define F6_GPIO_Port GPIOA
#define L6_Pin GPIO_PIN_7
#define L6_GPIO_Port GPIOA
#define F5_Pin GPIO_PIN_4
#define F5_GPIO_Port GPIOC
#define L5_Pin GPIO_PIN_5
#define L5_GPIO_Port GPIOC
#define F4_Pin GPIO_PIN_0
#define F4_GPIO_Port GPIOB
#define L4_Pin GPIO_PIN_1
#define L4_GPIO_Port GPIOB
#define F3_Pin GPIO_PIN_2
#define F3_GPIO_Port GPIOB
#define L3_Pin GPIO_PIN_10
#define L3_GPIO_Port GPIOB
#define F2_Pin GPIO_PIN_11
#define F2_GPIO_Port GPIOB
#define L2_Pin GPIO_PIN_12
#define L2_GPIO_Port GPIOB
#define F1_Pin GPIO_PIN_13
#define F1_GPIO_Port GPIOB
#define L1_Pin GPIO_PIN_14
#define L1_GPIO_Port GPIOB
#define EN_ALL_Pin GPIO_PIN_15
#define EN_ALL_GPIO_Port GPIOB
#define F9_Pin GPIO_PIN_8
#define F9_GPIO_Port GPIOC
#define L9_Pin GPIO_PIN_9
#define L9_GPIO_Port GPIOC
#define F10_Pin GPIO_PIN_8
#define F10_GPIO_Port GPIOA
#define REDE_Pin GPIO_PIN_11
#define REDE_GPIO_Port GPIOA
#define L10_Pin GPIO_PIN_12
#define L10_GPIO_Port GPIOA
#define F11_Pin GPIO_PIN_15
#define F11_GPIO_Port GPIOA
#define L11_Pin GPIO_PIN_10
#define L11_GPIO_Port GPIOC
#define F12_Pin GPIO_PIN_11
#define F12_GPIO_Port GPIOC
#define L12_Pin GPIO_PIN_12
#define L12_GPIO_Port GPIOC
#define F13_Pin GPIO_PIN_2
#define F13_GPIO_Port GPIOD
#define L13_Pin GPIO_PIN_3
#define L13_GPIO_Port GPIOB
#define F14_Pin GPIO_PIN_4
#define F14_GPIO_Port GPIOB
#define L14_Pin GPIO_PIN_5
#define L14_GPIO_Port GPIOB
#define F15_Pin GPIO_PIN_6
#define F15_GPIO_Port GPIOB
#define L15_Pin GPIO_PIN_7
#define L15_GPIO_Port GPIOB
#define F16_Pin GPIO_PIN_8
#define F16_GPIO_Port GPIOB
#define L16_Pin GPIO_PIN_9
#define L16_GPIO_Port GPIOB

/* USER CODE BEGIN Private defines */

/* USER CODE END Private defines */

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
