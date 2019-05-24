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


// this is the toolbar on the right side
var AppControls = (function () {

    var void_sw;
    var node;

    var initControls = function () {
        node = getElemById('app-controls');

        var controls_template = document.getElementById('app-controls-template');
        var contents = document.importNode(controls_template.content, true);
        node.appendChild(contents);

        var hsv = node.querySelector('#hsv');
        var hsl = node.querySelector('#hsl');

        var active = null;
        active = hsv;
        active.setAttribute('data-active', 'true');

        function switchPickingModeTo(elem) {
            active.removeAttribute('data-active');
            active = elem;
            active.setAttribute('data-active', 'true');
            setVoidSample();
            ColorPicker.setPickerMode('picker', active.textContent);
        };


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
            ColorPicker.setColor('picker', parseColor(color));
        };

        function dragStart(e) {
            e.dataTransfer.setData('sampleID', 'picker');
            e.dataTransfer.setData('location', 'picker');
            e.dataTransfer.setData('color', ColorPicker.getColor('picker').getHexa());
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

        var color = new Color();
        color.setHSL(0, 51, 51);
        ColorPicker.setColor('picker', color);

        setPickerDragAndDrop();
        initControls();
        setVoidSwitch();


        // Attach listeners to the other controls

        document.querySelector('#control-paste-state').addEventListener('click', function() {
            var state = prompt("Enter your state", "0:0/ffffff/1");
            if( state != null ) {
                ColorPickerSamples.pasteContainerState(state);
            }

        });

        var onServerAnswer = function(data) {
            ColorPickerSamples.pasteContainerState(data['color-string']);

            var img = document.getElementById('server-image');
            img.setAttribute('data-image-state','active')
            img.src = 'data:image/png;base64,' + data['image'];
        }


        document.querySelector('#control-connect-server').addEventListener(
            'click', function() {


            $.ajax({
                type: "GET",
                url: REST_GET_COLOR_STRING,
                success: success,
            });
        });

        document.querySelector('#control-send-server').addEventListener('click', function() {

            $.ajax({
                type: "POST",
                crossDomain: true,
                url: REST_SET_COLOR_STRING,
                success: onServerAnswer(),
                data: ColorPickerSamples.getContainerState(),
            });
        });


        document.querySelector('#copy-all').addEventListener('click', function() {
            var s = ColorPickerSamples.getContainerState();
            $('.toast').toast('show');
            // Copy string to clipboard
            navigator.clipboard.writeText(s);

        });


    };



    return {
        init : init,
        unsetVoidSample : unsetVoidSample,
        setVoidSample : setVoidSample,
    };

})();