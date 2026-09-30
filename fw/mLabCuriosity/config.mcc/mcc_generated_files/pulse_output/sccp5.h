/**
 * SCCP5 Generated Driver Header File 
 * 
 * @file	  sccp5.h
 * 
 * @ingroup   pulseoutputdriver
 * 
 * @brief 	  This is the generated driver header file for the SCCP5 driver
 *
 * @skipline @version   PLIB Version 1.2.3
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

#ifndef SCCP5_H
#define SCCP5_H


#ifdef __cplusplus
extern "C" {
#endif

// Section: Included Files

#include <stdint.h>
#include "pulseoutput_interface.h"

// Section: Data Type Definitions


/**
 * @ingroup  pulseoutputdriver
 * @brief    Structure object of type PULSEOUTPUT_INTERFACE with the custom name given by 
 *           the user in the Melody Driver User interface. The default name e.g. 
 *           Pulse_Output1 can be changed by the user in the MCCP user interface. 
 *           This allows defining a structure with application specific name using 
 *           the 'Custom Name' field. Application specific name allows the API Portability.
*/
extern const struct PULSEOUTPUT_INTERFACE Pulse_Output0;

/**
 * @ingroup  pulseoutputdriver
 * @brief    This macro defines the Custom Name for \ref SCCP5_PulseOutput_Initialize API
 */
#define Pulse_Output0_Initialize SCCP5_PulseOutput_Initialize
/**
 * @ingroup  pulseoutputdriver
 * @brief    This macro defines the Custom Name for \ref SCCP5_PulseOutput_Deinitialize API
 */
#define Pulse_Output0_Deinitialize SCCP5_PulseOutput_Deinitialize
/**
 * @ingroup  pulseoutputdriver
 * @brief    This macro defines the Custom Name for \ref SCCP5_PulseOutput_Enable API
 */
#define Pulse_Output0_Enable SCCP5_PulseOutput_Enable
/**
 * @ingroup  pulseoutputdriver
 * @brief    This macro defines the Custom Name for \ref SCCP5_PulseOutput_Disable API
 */
#define Pulse_Output0_Disable SCCP5_PulseOutput_Disable
/**
 * @ingroup  pulseoutputdriver
 * @brief    This macro defines the Custom Name for \ref SCCP5_PulseOutput_CountSet API
 */
#define Pulse_Output0_CountSet SCCP5_PulseOutput_CountSet
/**
 * @ingroup  pulseoutputdriver
 * @brief    This macro defines the Custom Name for \ref SCCP5_PulseOutput_SoftwareTriggerSet API
 */
#define Pulse_Output0_SoftwareTriggerSet SCCP5_PulseOutput_SoftwareTriggerSet
/**
 * @ingroup  pulseoutputdriver
 * @brief    This macro defines the Custom Name for \ref SCCP5_PulseOutput_Tasks API
 */
#define Pulse_Output0_Tasks SCCP5_PulseOutput_Tasks
/**
 * @ingroup  pulseoutputdriver
 * @brief    This macro defines the Custom Name for \ref SCCP5_PulseOutput_CallbackRegister API
 */
#define Pulse_Output0_PulseOutput_CallbackRegister SCCP5_PulseOutput_CallbackRegister
// Section: SCCP5 Module APIs

/**
 * @ingroup  pulseoutputdriver
 * @brief 	 Iitializes the SCCP5 PulseOutput driver. 
 *			 This function must be called before any other SCCP5 function is called.
 * @param    none
 * @return   none  
 */
void SCCP5_PulseOutput_Initialize( void );

/**
 * @ingroup  pulseoutputdriver
 * @brief    Deinitializes the SCCP5 to POR values
 * @param    none
 * @return   none  
 */
void SCCP5_PulseOutput_Deinitialize(void);

/**
 * @ingroup  pulseoutputdriver
 * @brief    Enables the SCCP5 module with the corresponding operation mode
 * @param    none
 * @return   none  
 */
void SCCP5_PulseOutput_Enable( void );

/**
 * @ingroup  pulseoutputdriver
 * @brief    Disables the SCCP5 module
 * @param    none
 * @return   none  
 */
void SCCP5_PulseOutput_Disable( void );

/**
 * @ingroup    pulseoutputdriver
 * @brief      Sets the ON delay and pulse width
 * @param[in]  onTime 	   -  16 bit pulse on time wait value
 * @param[in]  pulseCount  -  16 bit pulse width value  
 * @return     none  
 */
void SCCP5_PulseOutput_CountSet(uint16_t onTime, uint16_t pulseCount);

/**
 * @ingroup  pulseoutputdriver
 * @brief    This function sets the manual trigger
 * @param    none
 * @return   none      
 */
void SCCP5_PulseOutput_SoftwareTriggerSet( void );

/**
 * @ingroup    pulseoutputdriver
 * @brief      This function can be used to override default callback and to define 
 *             custom callback for SCCP5 PulseOutput event.
 * @param[in]  handler - Address of the callback function
 * @return     none  
 */
void SCCP5_PulseOutput_CallbackRegister(void (*handler)(void));

/**
 * @ingroup  pulseoutputdriver
 * @brief    This is the default callback with weak attribute. The user can 
 *           override and implement the default callback without weak attribute 
 *           or can register a custom callback function using  SCCP5_PulseOutput_CallbackRegister.
 * @param    none
 * @return   none  
 */
void SCCP5_PulseOutput_Callback(void);

/**
 * @ingroup  pulseoutputdriver
 * @brief    This function is used to implement the tasks for polled implementations
 * @param    none
 * @return   none  
 */
void SCCP5_PulseOutput_Tasks( void );

#ifdef __cplusplus
}
#endif

#endif //SCCP5_H
    
/**
 End of File
*/

