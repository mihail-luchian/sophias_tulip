'use strict';

var SAMPLES_PER_LINE = 5;
var NUM_STARTING_LINES = 4;
var DIGEST_UNIFIER = '/';

// this is the Whole color picker in the middle to the right
var UIColorPicker = (function UIColorPicker() {

	var subscribers = [];
	var pickers = [];


	/*========== Capture Mouse Movement ==========*/

	var setMouseTracking = function setMouseTracking(elem, callback) {
		elem.addEventListener('mousedown', function(e) {
			callback(e);
			document.getElementById("container-controls").setAttribute("expand-palette","false");
			document.addEventListener('mousemove', callback);
		});

		document.addEventListener('mouseup', function(e) {
            document.getElementById("container-controls").setAttribute("expand-palette","true");
			document.removeEventListener('mousemove', callback);
		});
	};

	/*====================*/
	// Color Picker Class
	/*====================*/

	function ColorPicker() {
		this.color = new Color();
		this.node = document.getElementById('color-picker');;
		this.subscribers = [];

		var type = this.node.getAttribute('data-mode');
		var topic = this.node.getAttribute('data-topic');

		this.topic = topic;
		this.picker_mode = (type === 'HSL') ? 'HSL' : 'HSV';
		this.color.setFormat(this.picker_mode);

		this.createPickingArea();
		this.createHueArea();

		this.newInputComponent('H', 'hue', this.inputChangeHue.bind(this));
		this.newInputComponent('S', 'saturation', this.inputChangeSaturation.bind(this));
		this.newInputComponent('V', 'value', this.inputChangeValue.bind(this));
		this.newInputComponent('L', 'lightness', this.inputChangeLightness.bind(this));

		this.newInputComponent('R', 'red', this.inputChangeRed.bind(this));
		this.newInputComponent('G', 'green', this.inputChangeGreen.bind(this));
		this.newInputComponent('B', 'blue', this.inputChangeBlue.bind(this));

		this.createPreviewBox();

		this.newInputComponent('hexa', 'hexa', this.inputChangeHexa.bind(this),'text');

		this.setColor(this.color);
		pickers[topic] = this;
	}

	/*************************************************************************/
	//				Function for generating the color-picker
	/*************************************************************************/

	ColorPicker.prototype.createPickingArea = function createPickingArea() {
		var area = document.createElement('div');
		var picker = document.createElement('div');

		area.className = 'picking-area';
		picker.className = 'picker';

		this.picking_area = area;
		this.color_picker = picker;
		setMouseTracking(area, this.updateColor.bind(this));

		area.appendChild(picker);
		this.node.appendChild(area);
	};

	ColorPicker.prototype.createHueArea = function createHueArea() {
		var area = document.createElement('div');
		var picker = document.createElement('div');

		area.className = 'hue';
		picker.className ='slider-picker';

		this.hue_area = area;
		this.hue_picker = picker;
		setMouseTracking(area, this.updateHueSlider.bind(this));

		area.appendChild(picker);
		this.node.appendChild(area);
	};


	ColorPicker.prototype.createPreviewBox = function createPreviewBox(e) {
		var preview_box = document.createElement('div');
		var preview_color = document.createElement('div');

		preview_box.className = 'preview';
		preview_color.className = 'preview-color';

		this.preview_color = preview_color;

		preview_box.appendChild(preview_color);
		this.node.appendChild(preview_box);
	};

	ColorPicker.prototype.newInputComponent = function newInputComponent(title, topic, onChangeFunc,type = 'number') {
		var wrapper = document.createElement('div');
		var input = document.createElement('input');
		var info = document.createElement('span');

		wrapper.className = 'input';
		wrapper.setAttribute('data-topic', topic);
		info.textContent = title;
		info.className = 'name';
		input.setAttribute('type', type);

		wrapper.appendChild(info);
		wrapper.appendChild(input);
		this.node.appendChild(wrapper);

		input.addEventListener('change', onChangeFunc);
		input.addEventListener('click', function() {
			this.select();
		});

		this.subscribe(topic, function(value) {
			input.value = value;
		});
	};


	/*************************************************************************/
	//					Updates properties of UI elements
	/*************************************************************************/

	ColorPicker.prototype.updateColor = function updateColor(e) {

		var x = e.clientX - this.picking_area.offsetLeft;
		var y = e.clientY - this.picking_area.offsetTop;
		var picker_offset = 5;

		// width and height should be the same
		var size = this.picking_area.clientWidth;

		if (x > size) x = size;
		if (y > size) y = size;
		if (x < 0) x = 0;
		if (y < 0) y = 0;

		var value = 100 - (y * 100 / size) | 0;
		var saturation = x * 100 / size | 0;

		if (this.picker_mode === 'HSV')
			this.color.setHSV(this.color.hue, saturation, value);
		if (this.picker_mode === 'HSL')
			this.color.setHSL(this.color.hue, saturation, value);

		this.color_picker.style.left = x - picker_offset + 'px';
		this.color_picker.style.top = y - picker_offset + 'px';

		this.updatePreviewColor();

		this.notify('value', value);
		this.notify('lightness', value);
		this.notify('saturation', saturation);

		this.notify('red', this.color.r);
		this.notify('green', this.color.g);
		this.notify('blue', this.color.b);
		this.notify('hexa', this.color.getHexa());

		notify(this.topic, this.color);
	};

	ColorPicker.prototype.updateHueSlider = function updateHueSlider(e) {
		var x = e.pageX - this.hue_area.offsetLeft;
		var width = this.hue_area.clientWidth;

		if (x < 0) x = 0;
		if (x > width) x = width;

		// TODO 360 => 359
		var hue = ((359 * x) / width) | 0;
		// if (hue === 360) hue = 359;

		this.updateSliderPosition(this.hue_picker, x);
		this.setHue(hue);
	};


	ColorPicker.prototype.setHue = function setHue(value) {
		this.color.setHue(value);

		this.updatePickerBackground();
		this.updatePreviewColor();

		this.notify('red', this.color.r);
		this.notify('green', this.color.g);
		this.notify('blue', this.color.b);
		this.notify('hexa', this.color.getHexa());
		this.notify('hue', this.color.hue);

		notify(this.topic, this.color);
	};

	// Updates when one of Saturation/Value/Lightness changes
	ColorPicker.prototype.updateSLV = function updateSLV() {
		this.updatePickerPosition();
		this.updatePreviewColor();

		this.notify('red', this.color.r);
		this.notify('green', this.color.g);
		this.notify('blue', this.color.b);
		this.notify('hexa', this.color.getHexa());

		notify(this.topic, this.color);
	};

	/*************************************************************************/
	//				Update positions of various UI elements
	/*************************************************************************/

	ColorPicker.prototype.updatePickerPosition = function updatePickerPosition() {
		var size = this.picking_area.clientWidth;
		var value = 0;
		var offset = 5;

		if (this.picker_mode === 'HSV')
			value = this.color.value;
		if (this.picker_mode === 'HSL')
			value = this.color.lightness;

		var x = (this.color.saturation * size / 100) | 0;
		var y = size - (value * size / 100) | 0;

		this.color_picker.style.left = x - offset + 'px';
		this.color_picker.style.top = y - offset + 'px';
	};

	ColorPicker.prototype.updateSliderPosition = function updateSliderPosition(elem, pos) {
		elem.style.left = Math.max(pos - 3, -2) + 'px';
	};

	ColorPicker.prototype.updateHuePicker = function updateHuePicker() {
		var size = this.hue_area.clientWidth;
		var offset = 1;
		var pos = (this.color.hue * size / 360 ) | 0;
		this.hue_picker.style.left = pos - offset + 'px';
	};


	/*************************************************************************/
	//						Update background colors
	/*************************************************************************/

	ColorPicker.prototype.updatePickerBackground = function updatePickerBackground() {
		var nc = new Color(this.color);
		nc.setHSV(nc.hue, 100, 100);
		this.picking_area.style.backgroundColor = nc.getHexa();
	};


	ColorPicker.prototype.updatePreviewColor = function updatePreviewColor() {
		this.preview_color.style.backgroundColor = this.color.getColor();
	};

	/*************************************************************************/
	//						Update input elements
	/*************************************************************************/

	ColorPicker.prototype.inputChangeHue = function inputChangeHue(e) {
		var value = parseInt(e.target.value);
		this.setHue(value);
		this.updateHuePicker();
	};

	ColorPicker.prototype.inputChangeSaturation = function inputChangeSaturation(e) {
		var value = parseInt(e.target.value);
		this.color.setSaturation(value);
		e.target.value = this.color.saturation;
		this.updateSLV();
	};

	ColorPicker.prototype.inputChangeValue = function inputChangeValue(e) {
		var value = parseInt(e.target.value);
		this.color.setValue(value);
		e.target.value = this.color.value;
		this.updateSLV();
	};

	ColorPicker.prototype.inputChangeLightness = function inputChangeLightness(e) {
		var value = parseInt(e.target.value);
		this.color.setLightness(value);
		e.target.value = this.color.lightness;
		this.updateSLV();
	};

	ColorPicker.prototype.inputChangeRed = function inputChangeRed(e) {
		var value = parseInt(e.target.value);
		this.color.setByName('r', value);
		e.target.value = this.color.r;
		this.setColor(this.color);
	};

	ColorPicker.prototype.inputChangeGreen = function inputChangeGreen(e) {
		var value = parseInt(e.target.value);
		this.color.setByName('g', value);
		e.target.value = this.color.g;
		this.setColor(this.color);
	};

	ColorPicker.prototype.inputChangeBlue = function inputChangeBlue(e) {
		var value = parseInt(e.target.value);
		this.color.setByName('b', value);
		e.target.value = this.color.b;
		this.setColor(this.color);
	};

	ColorPicker.prototype.inputChangeHexa = function inputChangeHexa(e) {
		var value = e.target.value;
		this.color.setHexa(value);
		this.setColor(this.color);
	};

	/*************************************************************************/
	//							Internal Pub/Sub
	/*************************************************************************/

	ColorPicker.prototype.subscribe = function subscribe(topic, callback) {
		this.subscribers[topic] = callback;
	};

	ColorPicker.prototype.notify = function notify(topic, value) {
		if (this.subscribers[topic])
			this.subscribers[topic](value);
	};

	/*************************************************************************/
	//							Set Picker Properties
	/*************************************************************************/

	ColorPicker.prototype.setColor = function setColor(color) {
		if(color instanceof Color !== true) {
			console.log('Typeof parameter not Color');
			return;
		}

		if (color.format !== this.picker_mode) {
			color.setFormat(this.picker_mode);
			color.updateHSX();
		}

		this.color.copy(color);
		this.updateHuePicker();
		this.updatePickerPosition();
		this.updatePickerBackground();
		this.updatePreviewColor();

		this.notify('red', this.color.r);
		this.notify('green', this.color.g);
		this.notify('blue', this.color.b);

		this.notify('hue', this.color.hue);
		this.notify('saturation', this.color.saturation);
		this.notify('value', this.color.value);
		this.notify('lightness', this.color.lightness);

		this.notify('hexa', this.color.getHexa());
		notify(this.topic, this.color);
	};

	ColorPicker.prototype.setPickerMode = function setPickerMode(mode) {
		if (mode !== 'HSV' && mode !== 'HSL')
			return;

		this.picker_mode = mode;
		this.node.setAttribute('data-mode', this.picker_mode);
		this.setColor(this.color);
	};

    // wrapper for the ColorPicker.prototype.setPickerMode function
	var setPickerMode = function setPickerMode(topic, mode) {
		if (pickers[topic]) {
            pickers[topic].setPickerMode(mode);
		}
	};

	var setColor = function setColor(topic, color) {
		if (pickers[topic])
			pickers[topic].setColor(color);
	};

	var getColor = function getColor(topic) {
		if (pickers[topic])
			return new Color(pickers[topic].color);
	};

	var subscribe = function subscribe(topic, callback) {
		if (subscribers[topic] === undefined)
			subscribers[topic] = [];

		subscribers[topic].push(callback);
	};

	var unsubscribe = function unsubscribe(callback) {
		subscribers.indexOf(callback);
		subscribers.splice(index, 1);
	};

	var notify = function notify(topic, value) {
		if (subscribers[topic] === undefined || subscribers[topic].length === 0)
			return;

		var color = new Color(value);
		for (var i in subscribers[topic])
			subscribers[topic][i](color);
	};

	var init = function init() {
        new ColorPicker();
	};

	return {
		init : init,
		setColor : setColor,
		getColor : getColor,
		subscribe : subscribe,
		unsubscribe : unsubscribe,
		setPickerMode : setPickerMode
	};

})();

window.addEventListener("load", function() {
	ColorPickerTool.init();
});

// this is the middle part of the UI
// the color sampling and management
var ColorPickerTool = (function ColorPickerTool() {

	/*========== Make an element resizable relative to it's parent ==========*/

	var UIComponent = (function UIComponent() {

		function makeResizable(elem, axis) {
			var valueX = 0;
			var valueY = 0;
			var action = 0;

			var resizeStart = function resizeStart(e) {
				e.stopPropagation();
				e.preventDefault();
				if (e.button !== 0)
					return;

				valueX = e.clientX - elem.clientWidth;
				valueY = e.clientY - elem.clientHeight;

				document.body.setAttribute('data-resize', axis);
				document.addEventListener('mousemove', mouseMove);
				document.addEventListener('mouseup', resizeEnd);
			};

			var mouseMove = function mouseMove(e) {
				if (action >= 0)
					elem.style.width = e.clientX - valueX + 'px';
				if (action <= 0)
					elem.style.height = e.clientY - valueY + 'px';
			};

			var resizeEnd = function resizeEnd(e) {
				if (e.button !== 0)
					return;

				document.body.removeAttribute('data-resize', axis);
				document.removeEventListener('mousemove', mouseMove);
				document.removeEventListener('mouseup', resizeEnd);
			};

			var handle = document.createElement('div');
			handle.className = 'resize-handle';

			if (axis === 'width') action = 1;
			else if (axis === 'height') action = -1;
			else axis = 'both';

			handle.className = 'resize-handle';
			handle.setAttribute('data-resize', axis);
			handle.addEventListener('mousedown', resizeStart);
			elem.appendChild(handle);
		};

		/*========== Make an element draggable relative to it's parent ==========*/

		var makeDraggable = function makeDraggable(elem, endFunction) {

			var offsetTop;
			var offsetLeft;

			elem.setAttribute('data-draggable', 'true');

			var dragStart = function dragStart(e) {
				e.preventDefault();
				e.stopPropagation();

				if (e.target.getAttribute('data-draggable') !== 'true' ||
					e.target !== elem || e.button !== 0)
					return;

				offsetLeft = e.clientX - elem.offsetLeft;
				offsetTop = e.clientY - elem.offsetTop;

				document.addEventListener('mousemove', mouseDrag);
				document.addEventListener('mouseup', dragEnd);
			};

			var dragEnd = function dragEnd(e) {
				if (e.button !== 0)
					return;

				document.removeEventListener('mousemove', mouseDrag);
				document.removeEventListener('mouseup', dragEnd);
			};

			var mouseDrag = function mouseDrag(e) {
				elem.style.left = e.clientX - offsetLeft + 'px';
				elem.style.top = e.clientY - offsetTop + 'px';
			};

			elem.addEventListener('mousedown', dragStart, false);
		};

		return {
			makeResizable : makeResizable,
			makeDraggable : makeDraggable
		};

	})();

	/*========== Color Class ==========*/

	/**
	 * ColorPalette
	 */
	// There are the things on top
	// the color pallettes on top, generated from the color in the ColorPicker area
	var ColorPalette = (function ColorPalette() {

		var samples = [];
		var color_palette;
		var complementary;

		var hideNode = function(node) {
			node.setAttribute('data-hidden', 'true');
		};

		var PaletteColorSample = function (id) {
			var node = document.createElement('div');
			node.className = 'palette-sample-color';

            // additional color sample information
			this.uid = samples.length;
			this.node = node;
			this.color = new Color();
			this.was_active = false;

			node.setAttribute('sample-id', this.uid);
			node.setAttribute('draggable', 'true');
			node.addEventListener('dragstart', this.dragStart.bind(this));
			node.addEventListener('click', this.pickColor.bind(this));

			samples.push(this);
		};


		PaletteColorSample.prototype.updateBgColor = function() {
			this.node.style.backgroundColor = this.color.getColor();
		};

		PaletteColorSample.prototype.updateColor = function(color) {
			this.color.copy(color);
			this.updateBgColor();
		};


		PaletteColorSample.prototype.updateHue = function (color, degree, steps) {
			this.color.copy(color);
			var hue = (steps * degree + this.color.hue) % 360;
			if (hue < 0) hue += 360;
			this.color.setHue(hue);
			this.updateBgColor();
		};

		PaletteColorSample.prototype.updateSaturation = function (
		    color, value, steps, total) {
			var saturation = color.saturation - value * (steps - Math.floor(total/2) );
			if ((saturation <= 0)|| (saturation > 100 )) {
				this.node.setAttribute('data-hidden', 'true');
				return;
			}

			if( (steps - Math.floor(total / 2)) == 0 ) {
			    this.node.setAttribute('data-working-color', 'true');
			}
			else {
			    this.node.setAttribute('data-working-color', 'false');
			}

			this.node.removeAttribute('data-hidden');
			this.color.copy(color);
			this.color.setSaturation(saturation);
			this.updateBgColor();
		};

		PaletteColorSample.prototype.updateLightness = function (
		    color, value, steps, total) {
			var lightness = color.lightness + value * (steps - Math.floor(total / 2));
			if ((lightness <= 0)|| (lightness > 100 )) {
				this.node.setAttribute('data-hidden', 'true');
				return;
			}

			if( (steps - Math.floor(total / 2)) == 0 ) {
			    this.node.setAttribute('data-working-color', 'true');
			}
			else {
			    this.node.setAttribute('data-working-color', 'false');
			}


			this.node.removeAttribute('data-hidden');
			this.color.copy(color);
			this.color.setLightness(lightness);
			this.updateBgColor();
		};

		PaletteColorSample.prototype.updateBrightness = function (
		    color, value, steps, total) {
			var brightness = color.value + value * (steps - Math.floor(total / 2));
			if ((brightness <= 0) || (brightness > 100 )) {
				this.node.setAttribute('data-hidden', 'true');
				return;
			}

            if( (steps - Math.floor(total / 2)) == 0 ) {
			    this.node.setAttribute('data-working-color', 'true');
			}
			else {
			    this.node.setAttribute('data-working-color', 'false');
			}


			this.node.removeAttribute('data-hidden');
			this.color.copy(color);
			this.color.setValue(brightness);
			this.updateBgColor();
		};


		PaletteColorSample.prototype.pickColor = function () {
			UIColorPicker.setColor('picker', this.color);
		};

		PaletteColorSample.prototype.dragStart = function (e) {
			e.dataTransfer.setData('sampleID', this.uid);
			e.dataTransfer.setData('location', 'palette-samples');
			e.dataTransfer.setData('color', this.color.getHexa());
		};

        // this is the general class for the palette on top
		var Palette = function Palette(text, size) {
			this.samples = [];
			this.locked = false;

            var container = document.createElement('div');
            container.className = 'palette-container';
            var palette_template = document.getElementById('palette-template');
            var palette = document.importNode(palette_template.content, true);
            container.appendChild(palette);

            var palette_samples = container.querySelector('.palette-samples');
            var title = container.querySelector('.title');
			title.textContent = text;
//
//
//			lock.addEventListener('click', function () {
//				this.locked = !this.locked;
//				lock.setAttribute('locked-state', this.locked);
//			}.bind(this));
//
			for(var i = 0; i < size; i++) {
				var sample = new PaletteColorSample();
				this.samples.push(sample);
				palette_samples.appendChild(sample.node);
			}

			this.container = container;
			this.title = title;
		};

		var createHuePalette = function createHuePalette() {
		    var samples_hue_palette = 24;
			var palette = new Palette('H', samples_hue_palette);

			UIColorPicker.subscribe('picker', function(color) {
				if (palette.locked === true)
					return;

				for(var i = 0; i < samples_hue_palette; i++) {
					palette.samples[i].updateHue(color, 5, i);
				}
			});

			color_palette.appendChild(palette.container);
		};

		var createSaturationPalette = function createSaturationPalette() {
		    var samples_sat_palette = 15;
			var palette = new Palette('S', samples_sat_palette);

			UIColorPicker.subscribe('picker', function(color) {
				if (palette.locked === true)
					return;

				for(var i = 0; i < samples_sat_palette; i++) {
					palette.samples[i].updateSaturation(color, -5, i, samples_sat_palette);
				}
			});

			color_palette.appendChild(palette.container);
		};

		/* Brightness or Lightness - depends on the picker mode */
		var createVLPalette = function createSaturationPalette() {
            var samples_vl_palette = 15;
			var palette = new Palette('L', samples_vl_palette);

			UIColorPicker.subscribe('picker', function(color) {
				if (palette.locked === true)
					return;

				if(color.format === 'HSL') {
					palette.title.textContent = 'L';
					for(var i = 0; i < samples_vl_palette; i++)
						palette.samples[i].updateLightness(color, -5, i, samples_vl_palette);
				}
				else {
					palette.title.textContent = 'V';
					for(var i = 0; i < samples_vl_palette; i++)
					{
					    palette.samples[i].updateBrightness(color, -5, i, samples_vl_palette);
					}

				}
			});

			color_palette.appendChild(palette.container);
		};

		var isBlankPalette = function isBlankPalette(container, value) {
			if (value === 0) {
				container.setAttribute('data-collapsed', 'true');
				return true;
			}

			container.removeAttribute('data-collapsed');
			return false;
		};


		var getSampleColor = function getSampleColor(id) {
			if (samples[id] !== undefined && samples[id]!== null)
				return new Color(samples[id].color);
		};

		var init = function init() {
			color_palette = getElemById('color-palettes');

			createHuePalette();
			createSaturationPalette();
			createVLPalette();

		};

		return {
			init : init,
			getSampleColor : getSampleColor
		};

	})();


	/**
	 * ColorPicker Samples
	 */
	// there are the sample colors that are managed in the middle area
	var ColorPickerSamples = (function ColorPickerSamples() {

		var samples = [];
        var lines = [];
		var nr_samples = 0;
		var active = null;
		var container = null;
		var add_btn;
		var add_btn_pos;

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
			Tool.unsetVoidSample();
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

			UIColorPicker.subscribe('picker', function(color) {
				if (active)
					active.updateColor(color);
			});

		};

		return {
			init : init,
			getSampleColor : getSampleColor,
			unsetActiveSample : unsetActiveSample,
			getStateAllLines : getStateAllLines,
			pasteContainerState : pasteContainerState,
			deleteContainerState : deleteContainerState
		};

	})();

	var StateButton = function StateButton(node, state) {
		this.state = false;
		this.callback = null;

		node.addEventListener('click', function() {
			this.state = !this.state;
			if (typeof this.callback === "function")
				this.callback(this.state);
		}.bind(this));
	};

	StateButton.prototype.set = function set() {
		this.state = true;
		if (typeof this.callback === "function")
			this.callback(this.state);
	};

	StateButton.prototype.unset = function unset() {
		this.state = false;
		if (typeof this.callback === "function")
			this.callback(this.state);
	};

	StateButton.prototype.subscribe = function subscribe(func) {
		this.callback = func;
	};


	/**
	 * Tool
	 */
	 // this is the toolbar on the right side
	var Tool = (function Tool() {

		var samples = [];
		var controls = null;
		var void_sw;
		var node;

		var initControls = function () {
			node = getElemById('app-controls');

            var tools_template = document.getElementById('tools-template');
            var contents = document.importNode(tools_template.content, true);
            node.appendChild(contents);

            var icon_paste_state = node.querySelector('#control-paste-state');
            var icon_connect_server = node.querySelector('#control-connect-server');
			var hsv = node.querySelector('#hsv');
			var hsl = node.querySelector('#hsl');
			var icon_copy_all = node.querySelector('#copy-all');

			var active = null;
			active = hsv;
			active.setAttribute('data-active', 'true');

			function switchPickingModeTo(elem) {
				active.removeAttribute('data-active');
				active = elem;
				active.setAttribute('data-active', 'true');
                setVoidSample();
				UIColorPicker.setPickerMode('picker', active.textContent);
			};


			icon_paste_state.addEventListener('click', function() {
                var state = prompt("Enter your state", "0:0/ffffff/1");
                if( state != null ) {
                    ColorPickerSamples.pasteContainerState(state);
                }

			});

			icon_connect_server.addEventListener('click', function() {

			    var success = function(data) {
                    ColorPickerSamples.pasteContainerState(data);
			    }

                $.ajax({
                  type: "GET",
                  url: REST_GET_COLOR_STRING,
                  success: success,
                });
			});

			icon_copy_all.addEventListener('click', function() {
				var s = ColorPickerSamples.getStateAllLines();
				$('.toast').toast('show');
				// Copy string to clipboard
				navigator.clipboard.writeText(s);

			});

			hsv.addEventListener('click', function() {
				switchPickingModeTo(hsv);
			});
			hsl.addEventListener('click', function() {
				switchPickingModeTo(hsl);
			});

		};

		var setPickerDragAndDrop = function setPickerDragAndDrop() {
			var preview = document.querySelector('#color-picker .preview-color');
			var picking_area = document.querySelector('#color-picker .picking-area');

			preview.setAttribute('draggable', 'true');
			preview.addEventListener('drop', drop);
			preview.addEventListener('dragstart', dragStart);
			preview.addEventListener('dragover', allowDropEvent);

			picking_area.addEventListener('drop', drop);
			picking_area.addEventListener('dragover', allowDropEvent);

			function drop(e) {
				var color = e.dataTransfer.getData('color');
				UIColorPicker.setColor('picker', parseColor(color));
			};

			function dragStart(e) {
				e.dataTransfer.setData('sampleID', 'picker');
				e.dataTransfer.setData('location', 'picker');
				e.dataTransfer.setData('color', UIColorPicker.getColor('picker').getHexa());
			};
		};

		var setVoidSwitch = function() {
			var void_sample = node.querySelector('#void-sample');
			void_sw = new StateButton(void_sample);
			void_sw.subscribe( function (state) {
				void_sample.setAttribute('data-active', state);
				if (state === true) {
					ColorPickerSamples.unsetActiveSample();
				}
			});
		};

		var unsetVoidSample = function() {
			void_sw.unset();
		};

        var setVoidSample = function() {
			void_sw.set();
		};

		var init = function init() {
			controls = getElemById('controls');

			var color = new Color();
			color.setHSL(0, 51, 51);
			UIColorPicker.setColor('picker', color);

			setPickerDragAndDrop();
			initControls();
			setVoidSwitch();
		};

		return {
			init : init,
			unsetVoidSample : unsetVoidSample,
			setVoidSample : setVoidSample,
		};

	})();

	var init = function init() {
		UIColorPicker.init();
		ColorPalette.init();
		ColorPickerSamples.init();
		Tool.init();
	};

	return {
		init : init
	};

})();
