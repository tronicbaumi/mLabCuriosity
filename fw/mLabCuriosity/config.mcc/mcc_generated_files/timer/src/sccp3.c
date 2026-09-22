/**
 * SCCP3-TIMER Generated Driver Source File
 * 
 * @file      sccp3.c
 * 
 * @ingroup   timerdriver
 * 
 * @brief     This is the generated driver source file for SCCP3-TIMER driver
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

// Section: Included Files

#include <stddef.h> 
#include "../sccp3.h"
#include "../timer_interface.h"

// Section: File specific functions

static void (*SCCP3_TimeoutHandler)(void) = NULL;

// Section: Driver Interface

// Defines an object for TIMER_INTERFACE

const struct TIMER_INTERFACE Timer3 = {
    .Initialize     = &SCCP3_Timer_Initialize,
    .Deinitialize   = &SCCP3_Timer_Deinitialize,
    .Start          = &SCCP3_Timer_Start,
    .Stop           = &SCCP3_Timer_Stop,
    .PeriodSet      = &SCCP3_Timer_PeriodSet,
    .PeriodGet	    = &SCCP3_Timer_PeriodGet,
    .CounterGet     = &SCCP3_Timer_CounterGet,
    .InterruptPrioritySet = &SCCP3_Timer_InterruptPrioritySet,
    .TimeoutCallbackRegister = &SCCP3_Timer_TimeoutCallbackRegister,
    .Tasks          = NULL,
};

// Section: Driver Interface Function Definitions

void SCCP3_Timer_Initialize(void)
{
    //MOD 16-Bit/32-Bit Timer; CCSEL disabled; T32 16 Bit; TMRPS 1:1; CLKSEL Standard Speed Peripheral Clock; TMRSYNC disabled; SIDL disabled; ON disabled; SYNC None; ALTSYNC disabled; ONESHOT disabled; TRIGEN disabled; OPS Each Time Base Period Match; RTRGEN disabled; OPSSRC Timer Interrupt Event; 
    CCP3CON1 = 0x0UL;
    //ASDG disabled; SSDG disabled; ASDGM disabled; PWMRSEN disabled; ICS ; AUXOUT Disabled; ICGSM Level-Sensitive mode; OCAEN disabled; OENSYNC disabled; 
    CCP3CON2 = 0x0UL;
    //PSSACE Tri-state; POLACE disabled; OSCNT None; OETRIG disabled; PSSBDF Tri-state; POLBDF disabled; 
    CCP3CON3 = 0x0UL;
    //ICOV disabled; SCEVT disabled; ASEVT disabled; TRCLR disabled; TRSET disabled; ICGARM disabled; RAWIP disabled; RBWIP disabled; TMRLWIP disabled; TMRHWIP disabled; PRLWIP disabled; 
    CCP3STAT = 0x0UL;
    //TMRL 0x0; TMRH 0x0; 
    CCP3TMR = 0x0UL;
    //PRL 7; PRH 0; 
    CCP3PR = 0x7UL;
    //BUFL 0x0; BUFH 0x0; 
    CCP3BUF = 0x0UL;
    //CMPA 0x0; 
    CCP3RA = 0x0UL;
    //CMPB 0x0; 
    CCP3RB = 0x0UL;
    
    SCCP3_Timer_TimeoutCallbackRegister(&SCCP3_TimeoutCallback);

    IFS1bits.CCT3IF = 0;
    // Enabling SCCP3 interrupt
    IEC1bits.CCT3IE = 1;

    CCP3CON1bits.ON = 1; //Enable Module
}

void SCCP3_Timer_Deinitialize(void)
{
    CCP3CON1bits.ON = 0;
    
    IFS1bits.CCT3IF = 0;
    IEC1bits.CCT3IE = 0;
    
    CCP3CON1 = 0x0UL; 
    CCP3CON2 = 0x1000000UL; 
    CCP3CON3 = 0x0UL; 
    CCP3STAT = 0x0UL; 
    CCP3TMR = 0x0UL; 
    CCP3PR = 0xFFFFFFFFUL; 
    CCP3BUF = 0x0UL; 
    CCP3RA = 0x0UL; 
    CCP3RB = 0x0UL; 
}

void SCCP3_Timer_Start(void)
{
    CCP3CON1bits.ON = 1;
}

void SCCP3_Timer_Stop(void)
{
    CCP3CON1bits.ON = 0;
}

void SCCP3_Timer_PeriodSet(uint32_t count)
{
    if(count > 0xFFFFU)
    {
        CCP3PR = count;
        CCP3CON1bits.T32 = 1;
    }
    else
    {
        CCP3PR = count;
        CCP3CON1bits.T32 = 0;
    }
}

void SCCP3_Timer_InterruptPrioritySet(enum INTERRUPT_PRIORITY priority)
{
    IPC6bits.CCT3IP = priority;
}

void SCCP3_Timer_TimeoutCallbackRegister(void (*handler)(void))
{
    if(NULL != handler)
    {
        SCCP3_TimeoutHandler = handler;
    }
}

void __attribute__ ((weak)) SCCP3_TimeoutCallback (void)
{ 

} 

/* cppcheck-suppress misra-c2012-8.4
*
* (Rule 8.4) REQUIRED: A compatible declaration shall be visible when an object or 
* function with external linkage is defined
*
* Reasoning: Interrupt declaration are provided by compiler and are available
* outside the driver folder
*/
void __attribute__ ( ( interrupt ) ) _CCT3Interrupt (void)
{
    if(NULL != SCCP3_TimeoutHandler)
    {
        (*SCCP3_TimeoutHandler)();
    }
    IFS1bits.CCT3IF = 0;
}

/**
 End of File
*/
