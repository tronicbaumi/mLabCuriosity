/* mLabCuriosity Blockly blocks + Python generators.
 *
 * Every hardware block generates a call on the `mlab` object that the
 * mLabScope Blockly tab injects when running the script (see BlocklyHAL in
 * mlab_scope.py). The blocks map to the same X2Cscope variables the Main tab
 * uses: mLabCuriosity.dpoN, dpiN, SW0, pwm_dcN, pwm_fN, adcN.
 */
(function () {
  'use strict';

  const gen = python.pythonGenerator;
  const Order = python.Order;

  const DO_CHANNELS = [['DO0', '0'], ['DO1', '1'], ['DO2', '2'], ['DO3', '3']];
  const DI_CHANNELS = [['DI0', '0'], ['DI1', '1'], ['DI2', '2'], ['DI3', '3'], ['SW0', 'SW0']];
  const PWM_CHANNELS = [['PWM0', '0'], ['PWM1', '1'], ['PWM2', '2'], ['PWM3', '3']];
  const ADC_CHANNELS = [['adc1', '1'], ['adc2', '2'], ['adc3', '3'], ['adc4', '4']];

  const COLOUR_DO = 20;
  const COLOUR_DI = 160;
  const COLOUR_PWM = 290;
  const COLOUR_ADC = 210;
  const COLOUR_TIME = 60;

  Blockly.defineBlocksWithJsonArray([
    // ---- Digital outputs ----
    {
      type: 'mlab_do_set',
      message0: 'set %1 to %2',
      args0: [
        { type: 'field_dropdown', name: 'CH', options: DO_CHANNELS },
        { type: 'input_value', name: 'VALUE', check: ['Boolean', 'Number'] },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: COLOUR_DO,
      tooltip: 'Write a digital output (mLabCuriosity.dpoN). true / non-zero = high.',
    },
    {
      type: 'mlab_do_toggle',
      message0: 'toggle %1',
      args0: [{ type: 'field_dropdown', name: 'CH', options: DO_CHANNELS }],
      previousStatement: null,
      nextStatement: null,
      colour: COLOUR_DO,
      tooltip: 'Invert a digital output.',
    },
    {
      type: 'mlab_do_get',
      message0: 'output %1 is high',
      args0: [{ type: 'field_dropdown', name: 'CH', options: DO_CHANNELS }],
      output: 'Boolean',
      colour: COLOUR_DO,
      tooltip: 'Read back the current state of a digital output.',
    },
    {
      type: 'mlab_level',
      message0: '%1',
      args0: [{ type: 'field_dropdown', name: 'LEVEL', options: [['HIGH', '1'], ['LOW', '0']] }],
      output: 'Boolean',
      colour: COLOUR_DO,
      tooltip: 'Logic level HIGH (true) or LOW (false).',
    },
    // ---- Digital inputs ----
    {
      type: 'mlab_di_read',
      message0: 'input %1 is high',
      args0: [{ type: 'field_dropdown', name: 'CH', options: DI_CHANNELS }],
      output: 'Boolean',
      colour: COLOUR_DI,
      tooltip: 'Read a digital input (mLabCuriosity.dpiN or SW0).',
    },
    {
      type: 'mlab_di_wait',
      message0: 'wait until %1 is %2',
      args0: [
        { type: 'field_dropdown', name: 'CH', options: DI_CHANNELS },
        { type: 'field_dropdown', name: 'LEVEL', options: [['HIGH', '1'], ['LOW', '0']] },
      ],
      previousStatement: null,
      nextStatement: null,
      colour: COLOUR_DI,
      tooltip: 'Block until the input reaches the given level.',
    },
    // ---- PWM ----
    {
      type: 'mlab_pwm_duty',
      message0: 'set %1 duty to %2 counts',
      args0: [
        { type: 'field_dropdown', name: 'CH', options: PWM_CHANNELS },
        { type: 'input_value', name: 'VALUE', check: 'Number' },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: COLOUR_PWM,
      tooltip: 'Write mLabCuriosity.pwm_dcN (0..65535).',
    },
    {
      type: 'mlab_pwm_duty_pct',
      message0: 'set %1 duty to %2 %%',
      args0: [
        { type: 'field_dropdown', name: 'CH', options: PWM_CHANNELS },
        { type: 'input_value', name: 'VALUE', check: 'Number' },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: COLOUR_PWM,
      tooltip: 'Duty cycle in percent (0..100).',
    },
    {
      type: 'mlab_pwm_freq',
      message0: 'set %1 frequency to %2 Hz',
      args0: [
        { type: 'field_dropdown', name: 'CH', options: PWM_CHANNELS },
        { type: 'input_value', name: 'VALUE', check: 'Number' },
      ],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: COLOUR_PWM,
      tooltip: 'PWM frequency in Hz (about 1221 Hz to 1 MHz, 80 MHz timer clock). Duty % is kept.',
    },
    {
      type: 'mlab_pwm_get',
      message0: '%1 %2',
      args0: [
        { type: 'field_dropdown', name: 'CH', options: PWM_CHANNELS },
        { type: 'field_dropdown', name: 'WHAT', options: [['duty [%]', 'duty'], ['frequency [Hz]', 'freq']] },
      ],
      output: 'Number',
      colour: COLOUR_PWM,
      tooltip: 'Read back PWM duty cycle in % or frequency in Hz.',
    },
    // ---- ADC ----
    {
      type: 'mlab_adc_read',
      message0: 'ADC %1',
      args0: [{ type: 'field_dropdown', name: 'CH', options: ADC_CHANNELS }],
      output: 'Number',
      colour: COLOUR_ADC,
      tooltip: 'Read the latest raw ADC value (mLabCuriosity.adcN).',
    },
    {
      type: 'mlab_adc_volts',
      message0: 'ADC %1 in volts',
      args0: [{ type: 'field_dropdown', name: 'CH', options: ADC_CHANNELS }],
      output: 'Number',
      colour: COLOUR_ADC,
      tooltip: 'Raw ADC value scaled to volts (12-bit, 3.3 V reference).',
    },
    // ---- Time ----
    {
      type: 'mlab_wait_ms',
      message0: 'wait %1 ms',
      args0: [{ type: 'input_value', name: 'MS', check: 'Number' }],
      inputsInline: true,
      previousStatement: null,
      nextStatement: null,
      colour: COLOUR_TIME,
      tooltip: 'Pause the script.',
    },
    {
      type: 'mlab_millis',
      message0: 'milliseconds since start',
      output: 'Number',
      colour: COLOUR_TIME,
      tooltip: 'Time since Run was pressed.',
    },
  ]);

  const ch = (block) => block.getFieldValue('CH');
  const quotedCh = (block) => {
    const c = ch(block);
    return /^\d+$/.test(c) ? c : "'" + c + "'";
  };

  gen.forBlock['mlab_do_set'] = function (block, g) {
    const v = g.valueToCode(block, 'VALUE', Order.NONE) || 'False';
    return 'mlab.set_do(' + ch(block) + ', ' + v + ')\n';
  };
  gen.forBlock['mlab_do_toggle'] = function (block) {
    return 'mlab.toggle_do(' + ch(block) + ')\n';
  };
  gen.forBlock['mlab_do_get'] = function (block) {
    return ['mlab.get_do(' + ch(block) + ')', Order.FUNCTION_CALL];
  };
  gen.forBlock['mlab_level'] = function (block) {
    return [block.getFieldValue('LEVEL') === '1' ? 'True' : 'False', Order.ATOMIC];
  };
  gen.forBlock['mlab_di_read'] = function (block) {
    return ['mlab.get_di(' + quotedCh(block) + ')', Order.FUNCTION_CALL];
  };
  gen.forBlock['mlab_di_wait'] = function (block) {
    const lvl = block.getFieldValue('LEVEL') === '1' ? 'True' : 'False';
    return 'mlab.wait_di(' + quotedCh(block) + ', ' + lvl + ')\n';
  };
  gen.forBlock['mlab_pwm_duty'] = function (block, g) {
    const v = g.valueToCode(block, 'VALUE', Order.NONE) || '0';
    return 'mlab.set_pwm_duty(' + ch(block) + ', ' + v + ')\n';
  };
  gen.forBlock['mlab_pwm_duty_pct'] = function (block, g) {
    const v = g.valueToCode(block, 'VALUE', Order.NONE) || '0';
    return 'mlab.set_pwm_duty_pct(' + ch(block) + ', ' + v + ')\n';
  };
  gen.forBlock['mlab_pwm_freq'] = function (block, g) {
    const v = g.valueToCode(block, 'VALUE', Order.NONE) || '1000';
    return 'mlab.set_pwm_freq(' + ch(block) + ', ' + v + ')\n';
  };
  gen.forBlock['mlab_pwm_get'] = function (block) {
    const fn = block.getFieldValue('WHAT') === 'duty' ? 'get_pwm_duty_pct' : 'get_pwm_freq';
    return ['mlab.' + fn + '(' + ch(block) + ')', Order.FUNCTION_CALL];
  };
  gen.forBlock['mlab_adc_read'] = function (block) {
    return ['mlab.read_adc(' + ch(block) + ')', Order.FUNCTION_CALL];
  };
  gen.forBlock['mlab_adc_volts'] = function (block) {
    return ['mlab.read_adc_volts(' + ch(block) + ')', Order.FUNCTION_CALL];
  };
  gen.forBlock['mlab_wait_ms'] = function (block, g) {
    const v = g.valueToCode(block, 'MS', Order.NONE) || '0';
    return 'mlab.wait_ms(' + v + ')\n';
  };
  gen.forBlock['mlab_millis'] = function () {
    return ['mlab.millis()', Order.FUNCTION_CALL];
  };

  gen.addReservedWords('mlab,check_stop,highlight');

  const num = (n) => ({ shadow: { type: 'math_number', fields: { NUM: n } } });

  window.MLAB_TOOLBOX = {
    kind: 'categoryToolbox',
    contents: [
      {
        kind: 'category', name: 'Outputs', colour: String(COLOUR_DO),
        contents: [
          { kind: 'block', type: 'mlab_do_set', inputs: { VALUE: { block: { type: 'mlab_level' } } } },
          { kind: 'block', type: 'mlab_do_toggle' },
          { kind: 'block', type: 'mlab_do_get' },
          { kind: 'block', type: 'mlab_level' },
        ],
      },
      {
        kind: 'category', name: 'Inputs', colour: String(COLOUR_DI),
        contents: [
          { kind: 'block', type: 'mlab_di_read' },
          { kind: 'block', type: 'mlab_di_wait' },
        ],
      },
      {
        kind: 'category', name: 'PWM', colour: String(COLOUR_PWM),
        contents: [
          { kind: 'block', type: 'mlab_pwm_duty_pct', inputs: { VALUE: num(50) } },
          { kind: 'block', type: 'mlab_pwm_duty', inputs: { VALUE: num(1000) } },
          { kind: 'block', type: 'mlab_pwm_freq', inputs: { VALUE: num(4000) } },
          { kind: 'block', type: 'mlab_pwm_get' },
        ],
      },
      {
        kind: 'category', name: 'ADC', colour: String(COLOUR_ADC),
        contents: [
          { kind: 'block', type: 'mlab_adc_read' },
          { kind: 'block', type: 'mlab_adc_volts' },
        ],
      },
      {
        kind: 'category', name: 'Time', colour: String(COLOUR_TIME),
        contents: [
          { kind: 'block', type: 'mlab_wait_ms', inputs: { MS: num(500) } },
          { kind: 'block', type: 'mlab_millis' },
        ],
      },
      { kind: 'sep' },
      {
        kind: 'category', name: 'Logic', categorystyle: 'logic_category',
        contents: [
          { kind: 'block', type: 'controls_if' },
          { kind: 'block', type: 'logic_compare' },
          { kind: 'block', type: 'logic_operation' },
          { kind: 'block', type: 'logic_negate' },
          { kind: 'block', type: 'logic_boolean' },
          { kind: 'block', type: 'logic_ternary' },
        ],
      },
      {
        kind: 'category', name: 'Loops', categorystyle: 'loop_category',
        contents: [
          { kind: 'block', type: 'controls_whileUntil',
            inputs: { BOOL: { shadow: { type: 'logic_boolean', fields: { BOOL: 'TRUE' } } } } },
          { kind: 'block', type: 'controls_repeat_ext', inputs: { TIMES: num(10) } },
          { kind: 'block', type: 'controls_for',
            inputs: { FROM: num(1), TO: num(10), BY: num(1) } },
          { kind: 'block', type: 'controls_flow_statements' },
        ],
      },
      {
        kind: 'category', name: 'Math', categorystyle: 'math_category',
        contents: [
          { kind: 'block', type: 'math_number' },
          { kind: 'block', type: 'math_arithmetic', inputs: { A: num(1), B: num(1) } },
          { kind: 'block', type: 'math_single' },
          { kind: 'block', type: 'math_round' },
          { kind: 'block', type: 'math_modulo', inputs: { DIVIDEND: num(64), DIVISOR: num(10) } },
          { kind: 'block', type: 'math_constrain',
            inputs: { LOW: num(0), HIGH: num(100) } },
          { kind: 'block', type: 'math_random_int', inputs: { FROM: num(1), TO: num(100) } },
          { kind: 'block', type: 'math_number_property' },
        ],
      },
      {
        kind: 'category', name: 'Text', categorystyle: 'text_category',
        contents: [
          { kind: 'block', type: 'text' },
          { kind: 'block', type: 'text_join' },
          { kind: 'block', type: 'text_print',
            inputs: { TEXT: { shadow: { type: 'text', fields: { TEXT: 'hello' } } } } },
        ],
      },
      { kind: 'category', name: 'Variables', categorystyle: 'variable_category', custom: 'VARIABLE' },
      { kind: 'category', name: 'Functions', categorystyle: 'procedure_category', custom: 'PROCEDURE' },
    ],
  };
})();
