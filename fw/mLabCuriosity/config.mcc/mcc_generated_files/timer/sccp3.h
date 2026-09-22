/**
 * SCCP3-TIMER Generated Driver Header File 
 * 
 * @file      sccp3.h
 * 
 * @ingroup   timerdriver
 * 
 * @brief     This is the generated driver header file for the SCCP3-TIMER driver
 *
 * @version   PLIB Version 1.2.3
 *
 * @skipline  Device : dsPIC33AK512MPS206
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

#ifndef SCCP3_H
#define SCCP3_H


#ifdef __cplusplus
extern "C" {
#endif

// Section: Included Files

#include <stddef.h>
#include <stdint.h>
#include <xc.h>
#include "timer_interface.h"

// Section: Data Type Definitions


/**
 * @ingroup  timerdriver
 * @brief    Structure object of type TIMER_INTERFACE with the custom name given by 
 *           the user in the Melody Driver User interface. The default name 
 *           e.g. Timer1 can be changed by the user in the TIMER user interface. 
 *           This allows defining a structure with application specific name using 
 *           the 'Custom Name' field. Application specific name allows the API Portability.
*/
extern const struct TIMER_INTERFACE Timer3;

/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_Initialize API
 */
#define Timer3_Initialize SCCP3_Timer_Initialize
/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_Deinitialize API
 */
#define Timer3_Deinitialize SCCP3_Timer_Deinitialize
/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_Tasks API
 */
#define Timer3_Tasks SCCP3_Timer_Tasks
/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_Start API
 */
#define Timer3_Start SCCP3_Timer_Start
/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_Stop API
 */
#define Timer3_Stop SCCP3_Timer_Stop

/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_PeriodSet API
 */
#define Timer3_PeriodSet SCCP3_Timer_PeriodSet
/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_PeriodGet API
 */
#define Timer3_PeriodGet SCCP3_Timer_PeriodGet
/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_CounterGet API
 */
#define Timer3_CounterGet SCCP3_Timer_CounterGet
/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_Counter16BitGet API
 */
#define Timer3_Counter16BitGet SCCP3_Timer_Counter16BitGet
/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_InterruptPrioritySet API
 */
#define Timer3_InterruptPrioritySet SCCP3_Timer_InterruptPrioritySet

/**
 * @ingroup  timerdriver
 * @brief    This macro defines the Custom Name for \ref SCCP3_Timer_TimeoutCallbackRegister API
 */
#define Timer3_TimeoutCallbackRegister SCCP3_Timer_TimeoutCallbackRegister

// Section: Driver Interface Functions

/**
 * @ingroup  timerdriver
 * @brief    Initializes the SCCP3 module 
 * @return   none  
 */
void SCCP3_Timer_Initialize (void);

/**
 * @ingroup  timerdriver
 * @brief    Deinitializes the SCCP3 to POR values
 * @return   none  
 */
void SCCP3_Timer_Deinitialize(void);

/**
 * @ingroup  timerdriver
 * @brief    Starts the timer
 * @pre      \ref SCCP3_Timer_Initialize must be called
 * @return   none  
 */
void SCCP3_Timer_Start(void);

/**
 * @ingroup  timerdriver
 * @brief    Stops the timer
 * @pre      \ref SCCP3_Timer_Initialize must be called
 * @return   none  
 */
void SCCP3_Timer_Stop(void);

/**
 * @ingroup  timerdriver
 * @brief    Sets the SCCP3-Timer period count value
 * @pre      \ref SCCP3_Timer_Initialize must be called
 * @param[in]  count - period value
 * @return   none  
 */
void SCCP3_Timer_PeriodSet(uint32_t count);

/**
 * @ingroup  timerdriver
 * @brief    This inline function gets the SCCP3-Timer period count value
 * @pre      \ref SCCP3_Timer_Initialize must be called
 * @return   Period count value  
 */
inline static uint32_t SCCP3_Timer_PeriodGet(void)
{
        return CCP3PR;
}

/**
 * @ingroup  timerdriver
 * @brief    This inline function gets the SCCP3-Timer elapsed count value
 * @return   Elapsed count value of the timer  
 */
inline static uint32_t SCCP3_Timer_CounterGet(void)
{
    return (uint32_t)CCP3TMR;
}

/**
 * @ingroup  timerdriver
 * @brief    This inline function gets the SCCP3-Timer least significant 16 bit elapsed count value
 * @return   Least significant 16 bit elapsed count value of the timer  
 */
inline static uint16_t SCCP3_Timer_Counter16BitGet(void)
{
    return (uint16_t)CCP3TMR;
}

/**
 * @ingroup  timerdriver
 * @brief    Sets the Interrupt Priority Value 
 * @return   none  
 */
void SCCP3_Timer_InterruptPrioritySet(enum INTERRUPT_PRIORITY priority);


/**
 * @ingroup    timerdriver
 * @brief      This function can be used to override default callback and to define 
 *             custom callback for SCCP3 Timeout event.
 * @param[in]  handler - Address of the callback function.  
 * @return     none 
 */
void SCCP3_Timer_TimeoutCallbackRegister(void (*handler)(void));

/**
 * @ingroup  timerdriver
 * @brief    This is the default callback with weak attribute. The user can 
 *           override and implement the default callback without weak attribute 
 *           or can register a custom callback function using  \ref SCCP3_Timer_TimeoutCallbackRegister.
 * @return   none  
 */
void SCCP3_TimeoutCallback(void);

#ifdef __cplusplus
}
#endif

#endif //SCCP3_H

/**
 End of File
*/


