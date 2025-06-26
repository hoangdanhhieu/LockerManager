#define WRITE_CHANNEL_CODE 0xE1
#define CONFIG_CODE 0xA1
#define READ_CONFIG_CODE 0xD0
#define WRITE_CONFIG_CODE 0xE0
#define BROADCAST_ADDRESS 0XFF
#define BOARDCAST_CODE 0xDF
#define HEADER 0XAA
#define TYPE_CODE 0xA1
#define READ_MCU_ID_CODE 0xDD
#define CPU_ID 0x1122334455AABB
#define READ_CHANNEL_STATUS_CODE 0xD1
#define READ_CHANNEL_SIGNAL_STATUS_CODE 0xD2
#define UNLOCK_CODE 0xE2
#define RUSC1_CODE 0xE4 //Running until Signal Changes to the Specified State and Stops
#define RUSC2_CODE 0xE5 //Running until Signal Changes to the Specified Times and Stops
#define RUSC3_CODE 0xE6 //Running until Signal Reaches the Specified State and Stops
#define MAX_CHANNEL 16
extern uint8_t ADDRESS;
extern uint32_t BAUD_RATE;
extern uint8_t UNLOCK_TIME;
