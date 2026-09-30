/**
 * PINS Generated Driver Header File 
 * 
 * @file      pins.h
 *            
 * @defgroup  pinsdriver Pins Driver
 *            
 * @brief     The Pin Driver directs the operation and function of 
 *            the selected device pins using dsPIC MCUs.
 *
 * @skipline @version   PLIB Version 1.0.5
 *
 * @skipline  Device : dsPIC33AK512MPS506
*/

/*
© [2026] Microchip Technology Inc. and its subsidiaries.

    Subject to your compliance with these terms, you may use Microchip 
    software and any derivatives exclusively with Microchip products. 
    You are responsible for complying with 3rd party license terms  
    applicable to your use of 3rd party software (including open source  
    software) that may accompany Microchip software. SOFTWARE IS ?AS IS.? 
    NO WARRANTIES, WHETHER EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS 
    SOFTWARE, INCLUDING ANY IMPLIED WARRANTIES OF NON-INFRINGEMENT,  
    MERCHANTABILITY, OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT 
    WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE, 
    INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY 
    KIND WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF 
    MICROCHIP HAS BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE 
    FORESEEABLE. TO THE FULLEST EXTENT ALLOWED BY LAW, MICROCHIP?S 
    TOTAL LIABILITY ON ALL CLAIMS RELATED TO THE SOFTWARE WILL NOT 
    EXCEED AMOUNT OF FEES, IF ANY, YOU PAID DIRECTLY TO MICROCHIP FOR 
    THIS SOFTWARE.
*/

#ifndef PINS_H
#define PINS_H
// Section: Includes
#include <xc.h>

/**
 * @ingroup  pinsdriver
 * @brief    Locks all the Peripheral Remapping registers and cannot be written.
 * @return   none  
 */
#define PINS_PPSLock()           (RPCONbits.IOLOCK = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Unlocks all the Peripheral Remapping registers and can be written.
 * @return   none  
 */
#define PINS_PPSUnlock()         (RPCONbits.IOLOCK = 0)

// Section: Device Pin Macros
/**
 * @ingroup  pinsdriver
 * @brief    Sets the RA3 GPIO Pin which has a custom name of DO0 to High
 * @pre      The RA3 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define DO0_SetHigh()          (_LATA3 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RA3 GPIO Pin which has a custom name of DO0 to Low
 * @pre      The RA3 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DO0_SetLow()           (_LATA3 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RA3 GPIO Pin which has a custom name of DO0
 * @pre      The RA3 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DO0_Toggle()           (_LATA3 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RA3 GPIO Pin which has a custom name of DO0
 * @param    none
 * @return   none  
 */
#define DO0_GetValue()         _RA3

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RA3 GPIO Pin which has a custom name of DO0 as Input
 * @param    none
 * @return   none  
 */
#define DO0_SetDigitalInput()  (_TRISA3 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RA3 GPIO Pin which has a custom name of DO0 as Output
 * @param    none
 * @return   none  
 */
#define DO0_SetDigitalOutput() (_TRISA3 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RA4 GPIO Pin which has a custom name of DO1 to High
 * @pre      The RA4 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define DO1_SetHigh()          (_LATA4 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RA4 GPIO Pin which has a custom name of DO1 to Low
 * @pre      The RA4 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DO1_SetLow()           (_LATA4 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RA4 GPIO Pin which has a custom name of DO1
 * @pre      The RA4 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DO1_Toggle()           (_LATA4 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RA4 GPIO Pin which has a custom name of DO1
 * @param    none
 * @return   none  
 */
#define DO1_GetValue()         _RA4

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RA4 GPIO Pin which has a custom name of DO1 as Input
 * @param    none
 * @return   none  
 */
#define DO1_SetDigitalInput()  (_TRISA4 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RA4 GPIO Pin which has a custom name of DO1 as Output
 * @param    none
 * @return   none  
 */
#define DO1_SetDigitalOutput() (_TRISA4 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RA5 GPIO Pin which has a custom name of DO2 to High
 * @pre      The RA5 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define DO2_SetHigh()          (_LATA5 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RA5 GPIO Pin which has a custom name of DO2 to Low
 * @pre      The RA5 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DO2_SetLow()           (_LATA5 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RA5 GPIO Pin which has a custom name of DO2
 * @pre      The RA5 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DO2_Toggle()           (_LATA5 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RA5 GPIO Pin which has a custom name of DO2
 * @param    none
 * @return   none  
 */
#define DO2_GetValue()         _RA5

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RA5 GPIO Pin which has a custom name of DO2 as Input
 * @param    none
 * @return   none  
 */
#define DO2_SetDigitalInput()  (_TRISA5 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RA5 GPIO Pin which has a custom name of DO2 as Output
 * @param    none
 * @return   none  
 */
#define DO2_SetDigitalOutput() (_TRISA5 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RA6 GPIO Pin which has a custom name of DO3 to High
 * @pre      The RA6 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define DO3_SetHigh()          (_LATA6 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RA6 GPIO Pin which has a custom name of DO3 to Low
 * @pre      The RA6 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DO3_SetLow()           (_LATA6 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RA6 GPIO Pin which has a custom name of DO3
 * @pre      The RA6 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DO3_Toggle()           (_LATA6 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RA6 GPIO Pin which has a custom name of DO3
 * @param    none
 * @return   none  
 */
#define DO3_GetValue()         _RA6

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RA6 GPIO Pin which has a custom name of DO3 as Input
 * @param    none
 * @return   none  
 */
#define DO3_SetDigitalInput()  (_TRISA6 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RA6 GPIO Pin which has a custom name of DO3 as Output
 * @param    none
 * @return   none  
 */
#define DO3_SetDigitalOutput() (_TRISA6 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RB9 GPIO Pin which has a custom name of DI3 to High
 * @pre      The RB9 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define DI3_SetHigh()          (_LATB9 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RB9 GPIO Pin which has a custom name of DI3 to Low
 * @pre      The RB9 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DI3_SetLow()           (_LATB9 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RB9 GPIO Pin which has a custom name of DI3
 * @pre      The RB9 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DI3_Toggle()           (_LATB9 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RB9 GPIO Pin which has a custom name of DI3
 * @param    none
 * @return   none  
 */
#define DI3_GetValue()         _RB9

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RB9 GPIO Pin which has a custom name of DI3 as Input
 * @param    none
 * @return   none  
 */
#define DI3_SetDigitalInput()  (_TRISB9 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RB9 GPIO Pin which has a custom name of DI3 as Output
 * @param    none
 * @return   none  
 */
#define DI3_SetDigitalOutput() (_TRISB9 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RB10 GPIO Pin which has a custom name of DI2 to High
 * @pre      The RB10 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define DI2_SetHigh()          (_LATB10 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RB10 GPIO Pin which has a custom name of DI2 to Low
 * @pre      The RB10 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DI2_SetLow()           (_LATB10 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RB10 GPIO Pin which has a custom name of DI2
 * @pre      The RB10 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DI2_Toggle()           (_LATB10 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RB10 GPIO Pin which has a custom name of DI2
 * @param    none
 * @return   none  
 */
#define DI2_GetValue()         _RB10

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RB10 GPIO Pin which has a custom name of DI2 as Input
 * @param    none
 * @return   none  
 */
#define DI2_SetDigitalInput()  (_TRISB10 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RB10 GPIO Pin which has a custom name of DI2 as Output
 * @param    none
 * @return   none  
 */
#define DI2_SetDigitalOutput() (_TRISB10 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RC3 GPIO Pin which has a custom name of SW0 to High
 * @pre      The RC3 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define SW0_SetHigh()          (_LATC3 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RC3 GPIO Pin which has a custom name of SW0 to Low
 * @pre      The RC3 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define SW0_SetLow()           (_LATC3 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RC3 GPIO Pin which has a custom name of SW0
 * @pre      The RC3 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define SW0_Toggle()           (_LATC3 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RC3 GPIO Pin which has a custom name of SW0
 * @param    none
 * @return   none  
 */
#define SW0_GetValue()         _RC3

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RC3 GPIO Pin which has a custom name of SW0 as Input
 * @param    none
 * @return   none  
 */
#define SW0_SetDigitalInput()  (_TRISC3 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RC3 GPIO Pin which has a custom name of SW0 as Output
 * @param    none
 * @return   none  
 */
#define SW0_SetDigitalOutput() (_TRISC3 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RC4 GPIO Pin which has a custom name of DI0 to High
 * @pre      The RC4 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define DI0_SetHigh()          (_LATC4 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RC4 GPIO Pin which has a custom name of DI0 to Low
 * @pre      The RC4 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DI0_SetLow()           (_LATC4 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RC4 GPIO Pin which has a custom name of DI0
 * @pre      The RC4 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DI0_Toggle()           (_LATC4 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RC4 GPIO Pin which has a custom name of DI0
 * @param    none
 * @return   none  
 */
#define DI0_GetValue()         _RC4

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RC4 GPIO Pin which has a custom name of DI0 as Input
 * @param    none
 * @return   none  
 */
#define DI0_SetDigitalInput()  (_TRISC4 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RC4 GPIO Pin which has a custom name of DI0 as Output
 * @param    none
 * @return   none  
 */
#define DI0_SetDigitalOutput() (_TRISC4 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RD0 GPIO Pin which has a custom name of LED0 to High
 * @pre      The RD0 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define LED0_SetHigh()          (_LATD0 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RD0 GPIO Pin which has a custom name of LED0 to Low
 * @pre      The RD0 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define LED0_SetLow()           (_LATD0 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RD0 GPIO Pin which has a custom name of LED0
 * @pre      The RD0 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define LED0_Toggle()           (_LATD0 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RD0 GPIO Pin which has a custom name of LED0
 * @param    none
 * @return   none  
 */
#define LED0_GetValue()         _RD0

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RD0 GPIO Pin which has a custom name of LED0 as Input
 * @param    none
 * @return   none  
 */
#define LED0_SetDigitalInput()  (_TRISD0 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RD0 GPIO Pin which has a custom name of LED0 as Output
 * @param    none
 * @return   none  
 */
#define LED0_SetDigitalOutput() (_TRISD0 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RD4 GPIO Pin which has a custom name of DI1 to High
 * @pre      The RD4 must be set as Output Pin             
 * @param    none
 * @return   none  
 */
#define DI1_SetHigh()          (_LATD4 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Sets the RD4 GPIO Pin which has a custom name of DI1 to Low
 * @pre      The RD4 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DI1_SetLow()           (_LATD4 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Toggles the RD4 GPIO Pin which has a custom name of DI1
 * @pre      The RD4 must be set as Output Pin
 * @param    none
 * @return   none  
 */
#define DI1_Toggle()           (_LATD4 ^= 1)

/**
 * @ingroup  pinsdriver
 * @brief    Reads the value of the RD4 GPIO Pin which has a custom name of DI1
 * @param    none
 * @return   none  
 */
#define DI1_GetValue()         _RD4

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RD4 GPIO Pin which has a custom name of DI1 as Input
 * @param    none
 * @return   none  
 */
#define DI1_SetDigitalInput()  (_TRISD4 = 1)

/**
 * @ingroup  pinsdriver
 * @brief    Configures the RD4 GPIO Pin which has a custom name of DI1 as Output
 * @param    none
 * @return   none  
 */
#define DI1_SetDigitalOutput() (_TRISD4 = 0)

/**
 * @ingroup  pinsdriver
 * @brief    Initializes the PINS module
 * @param    none
 * @return   none  
 */
void PINS_Initialize(void);



#endif
