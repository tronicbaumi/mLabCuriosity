/**
 * @file    uart_rxbuf.c
 * @brief   Interrupt-driven 64-byte receive ring buffers for UART2 and UART3.
 *
 * Single producer (RX ISR) / single consumer (main loop): the ISR only writes
 * head, the reader only writes tail, so no interrupt locking is needed.
 * head/tail are free-running 8-bit counters; 256 is a multiple of the buffer
 * size, so (head - tail) is always the fill level and (idx & MASK) the slot.
 * When the ring is full, new bytes are dropped and counted.
 */
#include <xc.h>
#include "uart_rxbuf.h"

#define UART_RXBUF_MASK (UART_RXBUF_SIZE - 1U)

#if ((UART_RXBUF_SIZE & UART_RXBUF_MASK) != 0U) || (UART_RXBUF_SIZE > 128U)
#error "UART_RXBUF_SIZE must be a power of two and <= 128"
#endif

typedef struct
{
    volatile uint8_t  buf[UART_RXBUF_SIZE];
    volatile uint8_t  head;      /* written by ISR only */
    volatile uint8_t  tail;      /* written by reader only */
    volatile uint16_t dropped;   /* ring full */
    volatile uint16_t overruns;  /* hardware RX FIFO overflow */
} UART_RXBUF_t;

static UART_RXBUF_t uart2Rx;
static UART_RXBUF_t uart3Rx;

static inline void RxPush(UART_RXBUF_t *rb, uint8_t data)
{
    uint8_t head = rb->head;
    if ((uint8_t)(head - rb->tail) >= UART_RXBUF_SIZE)
    {
        rb->dropped++;
    }
    else
    {
        rb->buf[head & UART_RXBUF_MASK] = data;
        rb->head = (uint8_t)(head + 1U);   /* publish after the data is stored */
    }
}

static inline uint8_t RxAvailable(const UART_RXBUF_t *rb)
{
    return (uint8_t)(rb->head - rb->tail);
}

static inline bool RxTryRead(UART_RXBUF_t *rb, uint8_t *data)
{
    uint8_t tail = rb->tail;
    if (tail == rb->head)
    {
        return false;
    }
    *data = rb->buf[tail & UART_RXBUF_MASK];
    rb->tail = (uint8_t)(tail + 1U);
    return true;
}

static inline void RxFlush(UART_RXBUF_t *rb)
{
    rb->tail = rb->head;
}

void UART_RXBUF_Initialize(void)
{
    uart2Rx.head = 0U; uart2Rx.tail = 0U; uart2Rx.dropped = 0U; uart2Rx.overruns = 0U;
    uart3Rx.head = 0U; uart3Rx.tail = 0U; uart3Rx.dropped = 0U; uart3Rx.overruns = 0U;

    /* Discard anything that arrived before the buffers were armed. */
    while (U2STATbits.RXBE == 0U) { (void)U2RXB; }
    while (U3STATbits.RXBE == 0U) { (void)U3RXB; }
    U2STATbits.RXFOIF = 0U;
    U3STATbits.RXFOIF = 0U;

    /* RXWM = 0 (MCC default): interrupt as soon as 1 byte is in the FIFO. */
    _U2RXIP = UART_RXBUF_IRQ_PRIO;
    _U3RXIP = UART_RXBUF_IRQ_PRIO;
    _U2RXIF = 0U;
    _U3RXIF = 0U;
    _U2RXIE = 1U;
    _U3RXIE = 1U;
}

void __attribute__((interrupt)) _U2RXInterrupt(void)
{
    while (U2STATbits.RXBE == 0U)
    {
        RxPush(&uart2Rx, (uint8_t)U2RXB);
    }
    if (U2STATbits.RXFOIF == 1U)
    {
        U2STATbits.RXFOIF = 0U;    /* receiver stalls until this is cleared */
        uart2Rx.overruns++;
    }
    _U2RXIF = 0U;
}

void __attribute__((interrupt)) _U3RXInterrupt(void)
{
    while (U3STATbits.RXBE == 0U)
    {
        RxPush(&uart3Rx, (uint8_t)U3RXB);
    }
    if (U3STATbits.RXFOIF == 1U)
    {
        U3STATbits.RXFOIF = 0U;
        uart3Rx.overruns++;
    }
    _U3RXIF = 0U;
}

// Section: UART2 API

uint8_t  UART2_RxAvailable(void)            { return RxAvailable(&uart2Rx); }
bool     UART2_RxTryRead(uint8_t *data)     { return RxTryRead(&uart2Rx, data); }
void     UART2_RxFlush(void)                { RxFlush(&uart2Rx); }
uint16_t UART2_RxDropCount(void)            { return uart2Rx.dropped; }
uint16_t UART2_RxOverrunCount(void)         { return uart2Rx.overruns; }

uint8_t UART2_RxRead(void)
{
    uint8_t data = 0U;
    (void)RxTryRead(&uart2Rx, &data);
    return data;
}

// Section: UART3 API

uint8_t  UART3_RxAvailable(void)            { return RxAvailable(&uart3Rx); }
bool     UART3_RxTryRead(uint8_t *data)     { return RxTryRead(&uart3Rx, data); }
void     UART3_RxFlush(void)                { RxFlush(&uart3Rx); }
uint16_t UART3_RxDropCount(void)            { return uart3Rx.dropped; }
uint16_t UART3_RxOverrunCount(void)         { return uart3Rx.overruns; }

uint8_t UART3_RxRead(void)
{
    uint8_t data = 0U;
    (void)RxTryRead(&uart3Rx, &data);
    return data;
}
