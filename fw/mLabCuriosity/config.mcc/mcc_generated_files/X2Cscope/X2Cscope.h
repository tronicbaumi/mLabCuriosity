/*
 * Copyright (c) 2013, Linz Center of Mechatronics GmbH (LCM) http://www.lcm.at/
 * All rights reserved.
 */
/*
 * This file is licensed according to the BSD 3-clause license as follows:
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *     * Redistributions of source code must retain the above copyright
 *       notice, this list of conditions and the following disclaimer.
 *     * Redistributions in binary form must reproduce the above copyright
 *       notice, this list of conditions and the following disclaimer in the
 *       documentation and/or other materials provided with the distribution.
 *     * Neither the name of the "Linz Center of Mechatronics GmbH" and "LCM" nor
 *       the names of its contributors may be used to endorse or promote products
 *       derived from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL "Linz Center of Mechatronics GmbH" BE LIABLE FOR ANY
 * DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 * ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
/*
 * This file is part of X2C. http://www.mechatronic-simulation.org/
 */
#ifndef X2CSCOPE_H
#define X2CSCOPE_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

//X2Cscope buffer size in bytes, uses the specified bytes from RAM
#ifndef X2CSCOPE_BUFFER_SIZE
#define X2CSCOPE_BUFFER_SIZE 16384
#endif

//X2Cscope Get Device Info service, 2 bytes
#ifndef X2CSCOPE_APP_VERSION
#define X2CSCOPE_APP_VERSION 0x0001
#endif

typedef struct compilationDate_type {
    char date[12];  /* __DATE__ is 11 chars + null terminator */
    char time[9];   /* __TIME__ is  8 chars + null terminator */
} compilationDate_t;

/* External X2Cscope API functions that must be used in the applications  */
void X2Cscope_Init(void); // Init X2Cscope and hook communication interfaces.
/* Below functions are implemented in X2Cscope library */
void X2Cscope_Communicate(void); // Communicate with X2Cscope GUI on PC side (Call in idle loop)
void X2Cscope_Update(void); // Sample point of scope functionality (Call with fixed periods)

#ifdef __cplusplus
}
#endif

#endif
