/**
 * SPI2 Generated Driver Source File
 * 
 * @file        spi2.c
 * 
 * @ingroup     spihostdriver
 * 
 * @brief       This is the generated driver source file for SPI2 driver.
 *
 * @skipline @version     PLIB Version 1.2.3
 *
 * @skipline    Device : dsPIC33AK512MPS206
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
#include "../spi2.h"

// Section: File specific data type definitions

/** 
 @ingroup spidriver
  @brief Dummy data to be sent for half duplex communication.
*/
#define SPI2_DUMMY_DATA 0x0

//Defines an object for SPI_HOST_INTERFACE.

const struct SPI_HOST_INTERFACE SPI2_Host = {
    .Initialize         = &SPI2_Initialize,
    .Deinitialize       = &SPI2_Deinitialize,
    .Close              = &SPI2_Close,
    .Open               = &SPI2_Open,
    .BufferExchange     = &SPI2_BufferExchange,
    .BufferRead         = &SPI2_BufferRead,
    .BufferWrite        = &SPI2_BufferWrite,
    .ByteExchange       = &SPI2_ByteExchange,
    .ByteRead           = &SPI2_ByteRead,    
    .ByteWrite          = &SPI2_ByteWrite,
    .IsRxReady          = &SPI2_IsRxReady,
    .IsTxReady          = &SPI2_IsTxReady,
};
        

/**
 @ingroup spihostdriver
 @struct SPI2_CONFIG 
 @brief Defines the SPI2 configuration.
*/
struct SPI2_HOST_CONFIG
{ 
    uint32_t controlRegister1; //SPI2BRG
    uint32_t controlRegister2; //SPI2CON1
};

static const struct SPI2_HOST_CONFIG config[] = {  
                                        { 
                                            /*Configuration setting for HOST_CONFIG.
                                            SPI Mode : Mode 1, Sampled at : Middle, Data Width : 8 Clock Frequency : 125 kHz*/
                                            0xf,//SPI2BRG
                                            0x21,//SPI2CON1
                                        },
                                    };

// Section: Driver Interface Function Definitions

void SPI2_Initialize (void)
{
    // WLENGTH 0x0; 
    SPI2CON2 = 0x0;
    // SPIROV disabled; FRMERR disabled; 
    SPI2STAT = 0x28;
    // SPIBUF 0x0; 
    SPI2BUF = 0x0;
    // SPIBRG 15; 
    SPI2BRG = 0xF;
    // SPIURDT 0x0; 
    SPI2URDT = 0x0;
    // ENHBUF enabled; SPIFE Frame Sync pulse precedes; MCLKEN Standard Speed Peripheral Clock; DISSCK disabled; DISSDI disabled; MSTEN Host; CKP Idle:Low, Active:High; SSEN disabled; CKE Idle to Active; SMP Middle; MODE16 disabled; MODE32 disabled; DISSDO disabled; SIDL disabled; ON disabled; FRMCNT 0x0; FRMSYPW One clock wide; MSSEN disabled; FRMPOL disabled; FRMSYNC disabled; FRMEN disabled; AUDMOD I2S; URDTEN disabled; AUDMONO stereo; IGNTUR disabled; IGNROV disabled; SPISGNEXT not sign-extended; AUDEN disabled; 
    SPI2CON1 = 0x21;
}

void SPI2_Deinitialize (void)
{
    SPI2_Close();
    
    SPI2CON1 = 0x0;
    SPI2CON2 = 0x0;
    SPI2STAT = 0x28;
    SPI2BUF = 0x0;
    SPI2BRG = 0x0;
    SPI2URDT = 0x0;
}

void SPI2_Close(void)
{
    SPI2CON1bits.ON = 0U;
}

bool SPI2_Open(uint8_t spiConfigIndex)
{
    bool status = false;
    if(!SPI2CON1bits.ON)
    {
        SPI2BRG = config[spiConfigIndex].controlRegister1;
        SPI2CON1 = config[spiConfigIndex].controlRegister2;
        SPI2CON1bits.ON = 1U;
        
        status = true;
    }
    return status;
}

uint8_t SPI2_ByteExchange(uint8_t byteData)
{
    while(1U == SPI2STATbits.SPITBF)
    {

    }

    SPI2BUF = byteData;

    while (1U == SPI2STATbits.SPIRBE)
    {
    
    }

    return (uint8_t)SPI2BUF;
}

void SPI2_BufferExchange(void *bufferData, size_t bufferSize)
{
    uint16_t dataSentCount = 0U;
    uint16_t dataReceivedCount = 0U;

    while(1U == SPI2STATbits.SPITBF)
    {

    }

    if (SPI2CON1bits.MODE32 == 1U)
    {
        // ---------------- 32-bit Mode  ----------------
        uint32_t *data = (uint32_t *)bufferData;
        bufferSize >>= 2U;

        while (dataSentCount < bufferSize)
        {
            if ( 1U != SPI2STATbits.SPITBF )
            {
                SPI2BUF = data[dataSentCount];
                dataSentCount++;
            }

            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
        while (dataReceivedCount < bufferSize)
        {
            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
    }
    else if(SPI2CON1bits.MODE16 == 1U)
    {
        // ---------------- 16-bit Mode --------------------
        uint16_t *data = (uint16_t *)bufferData;
        bufferSize >>= 1U;

        while (dataSentCount < bufferSize)
        {
            if ( 1U != SPI2STATbits.SPITBF )
            {
                SPI2BUF = data[dataSentCount];
                dataSentCount++;
            }

            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
        while (dataReceivedCount < bufferSize)
        {
            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
    }
    else
    {
        // ---------------- 8-bit Mode --------------------
        uint8_t *data = (uint8_t *)bufferData;

        while (dataSentCount < bufferSize)
        {
            if ( 1U != SPI2STATbits.SPITBF )
            {
                SPI2BUF = data[dataSentCount];
                dataSentCount++;
            }

            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
        while (dataReceivedCount < bufferSize)
        {
            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }

    }
}

void SPI2_BufferWrite(void *bufferData, size_t bufferSize)
{   
    uint16_t dataSentCount = 0U;
    uint16_t dataReceivedCount = 0U;
    
    while(1U == SPI2STATbits.SPITBF)
    {

    }

    if (SPI2CON1bits.MODE32 == 1U)
    {
        // ---------------- 32-bit Mode  ----------------
        uint32_t *data = (uint32_t *)bufferData;
        bufferSize >>= 2U;
        while (dataSentCount < bufferSize)
        {
            if ( 1U != SPI2STATbits.SPITBF )
            {
                SPI2BUF = data[dataSentCount];
                dataSentCount++;
            }

            if (0U == SPI2STATbits.SPIRBE)
            {
                (void)SPI2BUF; //Dummy Read
                dataReceivedCount++;
            }

        }
        while (dataReceivedCount < bufferSize)
        {
            if (0U == SPI2STATbits.SPIRBE)
            {
                (void)SPI2BUF; //Dummy Read
                dataReceivedCount++;
            }
        }   
    }
    else if(SPI2CON1bits.MODE16 == 1U)
    {
        // ---------------- 16-bit Mode --------------------
        uint16_t *data = (uint16_t *)bufferData;    
        bufferSize >>= 1;

        while (dataSentCount < bufferSize)
        {
            if ( 1U != SPI2STATbits.SPITBF )
            {
                SPI2BUF = data[dataSentCount];
                dataSentCount++;
            }

            if (0U == SPI2STATbits.SPIRBE)
            {
                (void)SPI2BUF; //Dummy Read
                dataReceivedCount++;
            }

        }
        while (dataReceivedCount < bufferSize)
        {
            if (0U == SPI2STATbits.SPIRBE)
            {
                (void)SPI2BUF; //Dummy Read
                dataReceivedCount++;
            }
        } 
    }
    else
    {
        // ---------------- 8-bit Mode --------------------
        uint8_t *data = (uint8_t *)bufferData;
        while (dataSentCount < bufferSize)
        {
            if ( 1U != SPI2STATbits.SPITBF )
            {
                SPI2BUF = data[dataSentCount];
                dataSentCount++;
            }

            if (0U == SPI2STATbits.SPIRBE)
            {
                (void)SPI2BUF; //Dummy Read
                dataReceivedCount++;
            }

        }
        while (dataReceivedCount < bufferSize)
        {
            if (0U == SPI2STATbits.SPIRBE)
            {
                (void)SPI2BUF; //Dummy Read
                dataReceivedCount++;
            }
        } 
    }
}

void SPI2_BufferRead(void *bufferData, size_t bufferSize)
{   
    uint16_t dataSentCount = 0U;
    uint16_t dataReceivedCount = 0U;
    
    while(1U == SPI2STATbits.SPITBF)
    {

    }

    if (SPI2CON1bits.MODE32 == 1U)
    {
        // ---------------- 32-bit Mode  ----------------
        uint32_t *data = (uint32_t *)bufferData;
        const uint32_t wData = SPI2_DUMMY_DATA;
        bufferSize >>= 2U;
        while (dataSentCount < bufferSize)
        {
            if ( 1U != SPI2STATbits.SPITBF )
            {
                SPI2BUF = wData;
                dataSentCount++;
            }

            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
        while (dataReceivedCount < bufferSize)
        {
            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
    }
    else if(SPI2CON1bits.MODE16 == 1U)
    {
        // ---------------- 16-bit Mode --------------------
        uint16_t *data = (uint16_t *)bufferData;  
        const uint16_t wData = SPI2_DUMMY_DATA;  
        bufferSize >>= 1;
        while (dataSentCount < bufferSize)
        {
            if ( 1U != SPI2STATbits.SPITBF )
            {
                SPI2BUF = wData;
                dataSentCount++;
            }

            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
        while (dataReceivedCount < bufferSize)
        {
            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
    }
    else
    {
        // ---------------- 8-bit Mode --------------------
        uint8_t *data = (uint8_t *)bufferData;
        const uint8_t wData = SPI2_DUMMY_DATA;

        while (dataSentCount < bufferSize)
        {
            if ( 1U != SPI2STATbits.SPITBF )
            {
                SPI2BUF = wData;
                dataSentCount++;
            }

            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
        while (dataReceivedCount < bufferSize)
        {
            if (0U == SPI2STATbits.SPIRBE)
            {
                data[dataReceivedCount] = SPI2BUF;
                dataReceivedCount++;
            }
        }
    }
}

void SPI2_ByteWrite(uint8_t byteData)
{
    while(1U == SPI2STATbits.SPITBF)
    {

    }
    
    SPI2BUF = byteData;
}

uint8_t SPI2_ByteRead(void)
{
    while (1U == SPI2STATbits.SPIRBE)
    {
    
    }
    
    return (uint8_t)SPI2BUF;
}

bool SPI2_IsRxReady(void)
{    
    return (!SPI2STATbits.SPIRBE);
}

bool SPI2_IsTxReady(void)
{    
    return (!SPI2STATbits.SPITBF);
}

