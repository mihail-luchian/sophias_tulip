// There are the things on top
// the color pallettes on top, generated from the color in the ColorPicker area
var ColorPalette = (function ColorPalette() {

    var samples = [];
    var color_palette;

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
        ColorPicker.setColor('picker', this.color);
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

        ColorPicker.subscribe('picker', function(color) {
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

        ColorPicker.subscribe('picker', function(color) {
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

        ColorPicker.subscribe('picker', function(color) {
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
