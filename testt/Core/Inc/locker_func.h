/*
 * locker_func.h
 *
 *  Created on: Jun 2, 2025
 *      Author: nonamezz
 */
#include "stdint.h"
void broadcast_func();
void getMCUID_func();
void writeChannel_func();
void readConfig_func();
void writeConfig_func();
void flash_init();
void readChannelStatus_func();
void readChannelSignalStatus_func();
void write_bit_to_num(uint32_t *num, uint8_t index, uint8_t value);
void writePin(uint8_t PIN, uint8_t value);
uint8_t readPin(uint8_t PIN);
void unlock_func();
void unlock_all();
void rusc1_func();
void rusc2_func();
void rusc3_func();
