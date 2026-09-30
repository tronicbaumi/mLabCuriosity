/**
 * SCCP5 Generated Driver Source File
 * 
 * @file 	  sccp5.c
 * 
 * @ingroup   pulseoutputdriver
 * 
 * @brief 	  This is the generated driver source file for SCCP5 driver
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
#include "../sccp5.h"

// Section: File specific functions

static void (*SCCP5_PulseOutputHandler)(void) = NULL;

// Section: Driver Interface

const struct PULSEOUTPUT_INTERFACE Pulse_Output0 = {
    .Initialize          = &SCCP5_PulseOutput_Initialize,
    .Deinitialize        = &SCCP5_PulseOutput_Deinitialize,
    .Enable              = &SCCP5_PulseOutput_Enable,
    .Disable             = &SCCP5_PulseOutput_Disable,
    .CountSet            = &SCCP5_PulseOutput_CountSet,
    .SoftwareTriggerSet  = &SCCP5_PulseOutput_SoftwareTriggerSet,
    .CallbackRegister = &SCCP5_PulseOutput_CallbackRegister,
    .Tasks               = &SCCP5_PulseOutput_Tasks
};

// Section: SCCP5 Module APIs

void SCCP5_PulseOutput_Initialize (void)
{
    // MOD Dual Edge Compare; CCSEL disabled; T32 16 Bit; TMRPS 1:4; CLKSEL Standard Speed Peripheral Clock; TMRSYNC disabled; SIDL disabled; ON disabled; SYNC None; ALTSYNC disabled; ONESHOT disabled; TRIGEN disabled; OPS Each Time Base Period Match; RTRGEN disabled; OPSSRC Timer Interrupt Event; 
    CCP5CON1 = 0x44UL;
    // ASDG disabled; SSDG disabled; ASDGM disabled; PWMRSEN disabled; ICS ; AUXOUT Disabled; ICGSM Level-Sensitive mode; OCAEN disabled; OENSYNC disabled; 
    CCP5CON2 = 0x0UL;
    // PSSACE Tri-state; POLACE disabled; OSCNT None; OETRIG disabled; PSSBDF Tri-state; POLBDF disabled; 
    CCP5CON3 = 0x0UL;
    // ICOV disabled; SCEVT disabled; ASEVT disabled; TRCLR disabled; TRSET disabled; ICGARM disabled; RAWIP disabled; RBWIP disabled; TMRLWIP disabled; TMRHWIP disabled; PRLWIP disabled; 
    CCP5STAT = 0x0UL;
    // TMRL 0x0; TMRH 0x0; 
    CCP5TMR = 0x0UL;
    // PRL 430000; PRH 0; 
    CCP5PR = 0x8FB0UL;
    // BUFL 0x0; BUFH 0x0; 
    CCP5BUF = 0x0UL;
    // CMPA 400000; 
    CCP5RA = 0x61A80UL;
    // CMPB 430000; 
    CCP5RB = 0x68FB0UL;
    
    SCCP5_PulseOutput_CallbackRegister(&SCCP5_PulseOutput_Callback);
    
    CCP5CON1bits.ON = 1; //Enable Module
}

void SCCP5_PulseOutput_Deinitialize (void)
{
    CCP5CON1bits.ON = 0;
    
    
    CCP5CON1 = 0x0UL;
    CCP5CON2 = 0x1000000UL;
    CCP5CON3 = 0x0UL;
    CCP5STAT = 0x0UL;
    CCP5TMR = 0x0UL;
    CCP5PR = 0xFFFFFFFFUL;
    CCP5BUF = 0x0UL;
    CCP5RA = 0x0UL;
    CCP5RB = 0x0UL;
}

void SCCP5_PulseOutput_Enable( void )
{
    CCP5CON1bits.ON = 1;
}


void SCCP5_PulseOutput_Disable( void )
{
    CCP5CON1bits.ON = 0;
}

void SCCP5_PulseOutput_CountSet(uint16_t onTime, uint16_t pulseCount)
{
    CCP5RB = onTime+pulseCount;
    CCP5RA = onTime;
    CCP5PR = onTime+pulseCount;
}

void SCCP5_PulseOutput_SoftwareTriggerSet( void )
{
    CCP5STATbits.TRSET = 1;
}

void SCCP5_PulseOutput_CallbackRegister(void (*handler)(void))
{
    if(NULL != handler)
    {
        SCCP5_PulseOutputHandler = handler;
    }
}

void __attribute__ ((weak)) SCCP5_PulseOutput_Callback ( void )
{ 

} 


void SCCP5_PulseOutput_Tasks( void )
{    
    if(IFS3bits.CCP5IF == 1)
    {
        // SCCP5 callback function 
        if(NULL != SCCP5_PulseOutputHandler)
        {
            (*SCCP5_PulseOutputHandler)();
        }
        IFS3bits.CCP5IF = 0;
    }
}
/**
 End of File
*/
