/**
 * @file    uart_rxbuf.h
 * @brief   Interrupt-driven 64-byte receive ring buffers for UART2 and UART3.
 *
 * Lives outside mcc_generated_files so an MCC regenerate does not remove it.
 * UART1 is reserved for X2Cscope and is not touched here.
 *
 * Usage:
 *   SYSTEM_Initialize();
 *   UART_RXBUF_Initialize();          // enables U2RX/U3RX interrupts
 *   ...
 *   while (UART2_RxAvailable() > 0U) { uint8_t b = UART2_RxRead(); ... }
 *
 * Once the buffers are running, do not call the polled MCC UART2_Read() /
 * UART3_Read(): the ISR owns the hardware RX FIFO. UARTx_Write() is unaffected.
 */
#ifndef UART_RXBUF_H
#define UART_RXBUF_H

#include <stdint.h>
#include <stdbool.h>

#define UART_RXBUF_SIZE       64U    /* must be a power of two, <= 128 */
#define UART_RXBUF_IRQ_PRIO   1U     /* same level as TMR1: never preempts the 200 kHz loop */

void     UART_RXBUF_Initialize(void);

uint8_t  UART2_RxAvailable(void);   /* bytes waiting, 0..64 */
uint8_t  UART2_RxRead(void);        /* next byte, or 0 when empty (check Available first) */
bool     UART2_RxTryRead(uint8_t *data);
void     UART2_RxFlush(void);
uint16_t UART2_RxDropCount(void);   /* bytes dropped because the ring was full */
uint16_t UART2_RxOverrunCount(void);/* hardware FIFO overruns (RXFOIF) */

uint8_t  UART3_RxAvailable(void);
uint8_t  UART3_RxRead(void);
bool     UART3_RxTryRead(uint8_t *data);
void     UART3_RxFlush(void);
uint16_t UART3_RxDropCount(void);
uint16_t UART3_RxOverrunCount(void);

#endif /* UART_RXBUF_H */
