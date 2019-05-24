'use strict';


/**
 * ColorPicker Samples
 */
// there are the sample colors that are managed in the middle area
var ColorPickerSamples = (function ColorPickerSamples() {

	var samples = [];
	var lines = [];
	var active = null;
	var container = null;

	var updateUI = function updateUI() {

		var nr = samples.length;
		for (var i=0; i < nr; i++)
			if (samples[i] !== null) {
				samples[i].updateBgColor();
			}

	};

	var setActivateSample = function setActivateSample(e) {
		if (e.target.parentNode.className !== 'sample')
			return;
		unsetActiveSample(active);
		AppControls.unsetVoidSample();
		active = samples[e.target.parentNode.getAttribute('sample-id')];
		active.activate();
	};

	var unsetActiveSample = function unsetActiveSample() {
		if (active)
			active.deactivate();
		active = null;
	};

	var getSampleColor = function getSampleColor(id) {
		if (samples[id] !== undefined && samples[id]!== null)
			return new Color(samples[id].color);
	};



	var SampleLine = function(container,line_id)  {

		var parent = document.createElement('div');
		parent.className = 'sample-line-parent'

		var line_template = document.getElementById('line-template');
		var line = document.importNode(line_template.content, true);
		parent.appendChild(line);

		var node = parent.querySelector('.sample-line');
		node.setAttribute('line-id', line_id);

		this.container = container;
		this.node = node;
		this.parent = parent;
		this.line_id = line_id;

		for (var i=0; i<SAMPLES_PER_LINE; i++) {
			var sample = new ColorSample(this,line_id*SAMPLES_PER_LINE+i);
			node.appendChild(sample.node);
			samples.push(sample);
		}

		// adding the line toolbar to the sample line
		var line_toolbar_template = document.getElementById('line-toolbar-template');
		var line_toolbar = document.importNode(line_toolbar_template.content, true);
		parent.querySelector('.line-toolbar').appendChild(line_toolbar);
		this.line_key_input = parent.querySelector('.line-key');

		parent.querySelector('.copy-line-state').addEventListener(
			'click', this.copyLineStateIconClick.bind(this));
		parent.querySelector('.delete-line-color').addEventListener(
			'click', this.deleteLineColorIconClick.bind(this));
		parent.querySelector('.delete-line-state').addEventListener(
			'click', this.deleteLineStateIconClick.bind(this));
		parent.querySelector('.paste-line-state').addEventListener(
			'click', this.pasteLineStateIconClick.bind(this));
		parent.querySelector('.paste-line-color').addEventListener(
			'click', this.pasteLineColorIconClick.bind(this));

	};

	SampleLine.prototype.getLineState = function() {
		var list_hex = [];
		var my_line = this.line_id;
		for (var i = 0; i < SAMPLES_PER_LINE; i++) {
			var current_sample_id = my_line*SAMPLES_PER_LINE + i;
			var hex = samples[current_sample_id].color.getSimpleHex();
			var digest = samples[current_sample_id].getDigest();
			if( hex !== "ffffff") {
				list_hex.push(digest);
			}
		}

		// Get key of the line
		var key_value = this.line_key_input.value;
		if( this.line_key_input.value.length == 0 ) {
			key_value = '' + this.line_id;
		}


		var final_string = '' + key_value + ':';
		if( list_hex.length > 0 ) {
			final_string = final_string + list_hex.join('-');
		} else {
			final_string = '';
		}


		return final_string;
	};

	SampleLine.prototype.copyLineStateIconClick = function (e) {
		navigator.clipboard.writeText(this.getLineState());
	};

	SampleLine.prototype.deleteLineColorIconClick = function (e) {
		var my_line = this.line_id;
		for (var i = 0; i < SAMPLES_PER_LINE; i++) {
			var current_sample_id = my_line*SAMPLES_PER_LINE + i;
			var hex = samples[current_sample_id].deleteColor();
		}

	};

	SampleLine.prototype.deleteLineStateIconClick = function (e) {
		this.deleteLineState();
	};

	SampleLine.prototype.deleteLineState = function() {
		this.line_key_input.value = ''
		var my_line = this.line_id;
		for (var i = 0; i < SAMPLES_PER_LINE; i++) {
			var current_sample_id = my_line*SAMPLES_PER_LINE + i;
			var hex = samples[current_sample_id].deleteState();
		}

	}


	SampleLine.prototype.pasteLineStateIconClick = function (e) {
		var states = prompt("Enter your state", "0/ffffff/");
		if( states != null ) {
			this.pasteLineState(states);
		}

	};


	SampleLine.prototype.pasteLineState = function (state) {

		if( state.includes(':') ) {
			var line_state = parseLineState(state);
			var key = line_state[0];
			this.line_key_input.value = key;

			var s = line_state[1];
			var l = s.length;
			for( var i = 0; i < l; i++) {
				var state = s[i];
				samples[this.line_id*SAMPLES_PER_LINE+i].updateState(state);
			}
		} else {
			var s = parseStates(state);
			var l = s.length;
			for( var i = 0; i < l; i++) {
				var state = s[i];
				samples[this.line_id*SAMPLES_PER_LINE+i].updateState(state);
			}
		}


	};


	SampleLine.prototype.pasteLineColorIconClick = function (e) {
		var colors = prompt("Enter your state", "ffffff");
		if( colors != null ) {
			this.pasteLineColors(colors);
		}

	};


	SampleLine.prototype.pasteLineColors = function (s) {
		var s = parseColors(colors);
		var l = s.length;

		for( var i = 0; i < SAMPLES_PER_LINE; i++) {
			var color = s[i];
			samples[this.line_id*SAMPLES_PER_LINE+i].updateColor(color);
		}
	};

	SampleLine.prototype.updateSample = function (sample_id,digest) {
		samples[sample_id].updateState(parseState(digest));
	};

	var getStateAllLines = function () {
		var list_line_states = [];

		for(var i = 0; i<NUM_STARTING_LINES; i++) {
		   var state =  lines[i].getLineState();
		   if( state.length > 0 ) {
			  list_line_states.push( state );
		   }
		}

		return list_line_states.join(',');

	}

	var pasteContainerState = function (state) {
		deleteContainerState();

		var list_string = state.trim().split(',');
		var l = list_string.length;
		for( var i = 0; i < l; i++) {
			lines[i].pasteLineState(list_string[i]);
		}

	}

	var deleteContainerState = function (state) {

		var l = lines.length;
		for( var i = 0; i < l; i++) {
			lines[i].deleteLineState();
		}

	}

	var init = function init() {
		container = getElemById('container-samples');

		// Adding lines with samples to the picker
		for (var line=0; line<NUM_STARTING_LINES; line++) {

			var sampleLine = new SampleLine(this,line);
			container.appendChild(sampleLine.parent);
			lines.push(sampleLine);
		}


		updateUI();

		active = samples[0];
		active.activate();

		container.addEventListener('click', setActivateSample);

		ColorPicker.subscribe('picker', function(color) {
			if (active)
				active.updateColor(color);
		});

	};

	return {
		init : init,
		getSampleColor : getSampleColor,
		unsetActiveSample : unsetActiveSample,
		getContainerState : getStateAllLines,
		pasteContainerState : pasteContainerState,
		deleteContainerState : deleteContainerState
	};

})();






