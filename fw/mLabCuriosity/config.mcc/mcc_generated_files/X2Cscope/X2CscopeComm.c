/* ************************************************************************** */
/** X2CComm.c

  @Company
    Microchip Technology

  @Summary
    Implements the X2C Lin protocol connection with MCC Peripheral drivers.

 */
/* ************************************************************************** */
#include <xc.h>
#include "X2CscopeComm.h"
#include "../uart/uart1.h" 
#include "../uart/uart2.h" 
#include "../uart/uart3.h" 


/** 
  @brief
    Puts the data to the hardware layer. (UART)
   @param[in] serial Serial interface object. (Not used)
   @param[in] data Data to send 
 */
void sendSerial(uint8_t data)
{
    X2CScopeUart.Write(data);
}

/** 
  @brief
   Get serial data from hardware. Reset the hardware in case of error. (UART2)
  @param[in] serial Serial interface object. (Not used)
  @return
    Return with the received data
 */
uint8_t receiveSerial()
{
    return X2CScopeUart.Read();
}

/** 
  @brief  Check data availability (UART).
  @param[in] serial Serial interface object. (Not used)
  @return
    True -> Serial data ready to read.
    False -> No data.
 */
uint8_t isReceiveDataAvailable()
{
    return X2CScopeUart.IsRxReady();
}

/** 
  @brief
   Check output buffer. (UART)
  @param[in] serial Serial interface object. (Not used)
  @return    
    True -> Transmit buffer is not full, at least one more character can be written.
    False -> Transmit buffer is full.
 */
uint8_t isSendReady()
{
    return X2CScopeUart.IsTxReady();
}


/** 
  @brief
    Flush the transmit buffer. This function is called when LNet frame is complete.
   @param[in] serial Serial interface object. (Not used)
   @param[in] data Data to send 
 */
void flushSerial(void)
{
//#error "Implement your flush function, then delete this line."
/* Example:
 * If no extra handling is required, leave this function empty.
 * If using a buffer to send data, implement the buffer send/flush here.
 */
}

/**
 * @brief Comm-layer post-init, called from X2Cscope_Init() after
 * X2Cscope_InitialiseEx(). Enable the UART TX interrupt here if using
 * interrupt-driven transmission. Leave empty if not needed.
 */
void X2CscopeComm_PostInit(void)
{
    /* Example: enable UART TX interrupt for interrupt-driven TX.
     * IEC0bits.U1TXIE = 1;
     */
}
/* *****************************************************************************
 End of File
 */