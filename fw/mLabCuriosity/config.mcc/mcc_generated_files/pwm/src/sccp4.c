/**
 * SCCP4 Generated Driver Source File
 * 
 * @file 	  sccp4.c
 * 
 * @ingroup   pwmdriver
 * 
 * @brief 	  This is the generated driver source file for SCCP4 driver
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

// Section: Included Files

#include <xc.h>
#include <stddef.h>
#include "../sccp4.h"

// Section: File specific functions

static void (*SCCP4_PWMHandler)(void) = NULL;

// Section: Driver Interface

const struct PWM_INTERFACE PWM3 = {
    .Initialize          = &SCCP4_PWM_Initialize,
    .Deinitialize        = &SCCP4_PWM_Deinitialize,
    .Enable              = &SCCP4_PWM_Enable,
    .Disable             = &SCCP4_PWM_Disable,
    .PeriodSet           = &SCCP4_PWM_PeriodSet,
    .DutyCycleSet        = &SCCP4_PWM_DutyCycleSet,
    .SoftwareTriggerSet  = &SCCP4_PWM_SoftwareTriggerSet,
    .DeadTimeSet         = NULL,
    .OutputModeSet       = NULL,
    .CallbackRegister = &SCCP4_PWM_CallbackRegister,
    .Tasks               = &SCCP4_PWM_Tasks
};

// Section: SCCP4 Module APIs

void SCCP4_PWM_Initialize (void)
{
    // MOD Dual Edge Compare, Buffered(PWM); CCSEL disabled; T32 16 Bit; TMRPS 1:1; CLKSEL Standard Speed Peripheral Clock; TMRSYNC disabled; SIDL disabled; ON disabled; SYNC None; ALTSYNC disabled; ONESHOT disabled; TRIGEN disabled; OPS Each Time Base Period Match; RTRGEN disabled; OPSSRC Timer Interrupt Event; 
    CCP4CON1 = 0x5UL;
    // ASDG disabled; SSDG disabled; ASDGM disabled; PWMRSEN disabled; ICS ; AUXOUT Disabled; ICGSM Level-Sensitive mode; OCAEN enabled; OENSYNC disabled; 
    CCP4CON2 = 0x1000000UL;
    // PSSACE Tri-state; POLACE disabled; OSCNT None; OETRIG disabled; PSSBDF Tri-state; POLBDF disabled; 
    CCP4CON3 = 0x0UL;
    // ICOV disabled; SCEVT disabled; ASEVT disabled; TRCLR disabled; TRSET disabled; ICGARM disabled; RAWIP disabled; RBWIP disabled; TMRLWIP disabled; TMRHWIP disabled; PRLWIP disabled; 
    CCP4STAT = 0x0UL;
    // TMRL 0x0; TMRH 0x0; 
    CCP4TMR = 0x0UL;
    // PRL 65535; PRH 0; 
    CCP4PR = 0xFFFFUL;
    // BUFL 0x0; BUFH 0x0; 
    CCP4BUF = 0x0UL;
    // CMPA 0; 
    CCP4RA = 0x0UL;
    // CMPB 65535; 
    CCP4RB = 0xFFFFUL;
    SCCP4_PWM_CallbackRegister(&SCCP4_PWM_Callback);
    
    CCP4CON1bits.ON = 1; //Enable Module
}

void SCCP4_PWM_Deinitialize (void)
{
    CCP4CON1bits.ON = 0;
    
    CCP4CON1 = 0x0UL;
    CCP4CON2 = 0x1000000UL;
    CCP4CON3 = 0x0UL;
    CCP4STAT = 0x0UL;
    CCP4TMR = 0x0UL;
    CCP4PR = 0xFFFFFFFFUL;
    CCP4BUF = 0x0UL;
    CCP4RA = 0x0UL;
    CCP4RB = 0x0UL;
}

void SCCP4_PWM_Enable( void )
{
    CCP4CON1bits.ON = 1;
}


void SCCP4_PWM_Disable( void )
{
    CCP4CON1bits.ON = 0;
}

void SCCP4_PWM_PeriodSet(size_t periodCount)
{
    CCP4PR = periodCount;
}

void SCCP4_PWM_DutyCycleSet(size_t dutyCycleCount)
{
    CCP4RB = dutyCycleCount;
}

void SCCP4_PWM_SoftwareTriggerSet( void )
{
    CCP4STATbits.TRSET = 1;
}

void SCCP4_PWM_CallbackRegister(void (*handler)(void))
{
    if(NULL != handler)
    {
        SCCP4_PWMHandler = handler;
    }
}

void __attribute__ ((weak)) SCCP4_PWM_Callback ( void )
{ 

} 


void SCCP4_PWM_Tasks( void )
{    
    if(IFS1bits.CCT4IF == 1)
    {
        // SCCP4 callback function 
        if(NULL != SCCP4_PWMHandler)
        {
            (*SCCP4_PWMHandler)();
        }
        IFS1bits.CCT4IF = 0;
    }
}
/**
 End of File
*/
