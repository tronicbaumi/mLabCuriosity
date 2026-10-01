/**
 * PINS Generated Driver Source File 
 * 
 * @file      pins.c
 *            
 * @ingroup   pinsdriver
 *            
 * @brief     This is the generated driver source file for PINS driver.
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

// Section: Includes
#include <xc.h>
#include <stddef.h>
#include "../pins.h"

// Section: File specific functions

// Section: Driver Interface Function Definitions
void PINS_Initialize(void)
{
    /****************************************************************************
     * Setting the Output Latch SFR(s)
     ***************************************************************************/
    LATA = 0x0000UL;
    LATB = 0x0020UL;
    LATC = 0x0400UL;
    LATD = 0x0080UL;

    /****************************************************************************
     * Setting the GPIO Direction SFR(s)
     ***************************************************************************/
    TRISA = 0x0F87UL;
    TRISB = 0x0EDBUL;
    TRISC = 0x0BBFUL;
    TRISD = 0x0172UL;


    /****************************************************************************
     * Setting the Weak Pull Up and Weak Pull Down SFR(s)
     ***************************************************************************/
    CNPUA = 0x0000UL;
    CNPUB = 0x0000UL;
    CNPUC = 0x0008UL;
    CNPUD = 0x0000UL;
    CNPDA = 0x0078UL;
    CNPDB = 0x0600UL;
    CNPDC = 0x0010UL;
    CNPDD = 0x0010UL;


    /****************************************************************************
     * Setting the Open Drain SFR(s)
     ***************************************************************************/
    ODCA = 0x0000UL;
    ODCB = 0x0000UL;
    ODCC = 0x0000UL;
    ODCD = 0x0000UL;


    /****************************************************************************
     * Setting the Analog/Digital Configuration SFR(s)
     ***************************************************************************/
    ANSELA = 0x0F87UL;
    ANSELB = 0x00C2UL;

    /****************************************************************************
     * Set the PPS
     ***************************************************************************/
      PINS_PPSUnlock(); // unlock PPS

        RPINR13bits.U2RXR = 0x001CUL; //RB11->UART2:U2RX;
        RPINR14bits.U3RXR = 0x0011UL; //RB0->UART3:U3RX;
        RPINR13bits.U1RXR = 0x002CUL; //RC11->UART1:U1RX;
        RPINR14bits.SDI1R = 0x0028UL; //RC7->SPI1:SDI1;
        RPOR12bits.RP52R = 0x0028UL;  //RD3->SCCP2:OCM2;
        RPOR12bits.RP51R = 0x0027UL;  //RD2->SCCP1:OCM1;
        RPOR6bits.RP25R = 0x002AUL;  //RB8->SCCP4:OCM4;
        RPOR4bits.RP19R = 0x0029UL;  //RB2->SCCP3:OCM3;
        RPOR5bits.RP22R = 0x0015UL;  //RB5->UART2:U2TX;
        RPOR13bits.RP56R = 0x0017UL;  //RD7->UART3:U3TX;
        RPOR10bits.RP43R = 0x0013UL;  //RC10->UART1:U1TX;
        RPOR9bits.RP39R = 0x0019UL;  //RC6->SPI1:SDO1;
        RPINR14bits.SCK1R = 0x0037UL;  //RD6->SPI1:SCK1IN;
        RPOR13bits.RP55R = 0x001AUL;  //RD6->SPI1:SCK1OUT;

      PINS_PPSLock(); // lock PPS


}

