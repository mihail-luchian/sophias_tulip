var StateButton = function StateButton(node, func) {
    this.state = false;
    this.callback = func;

    node.addEventListener('click', function() {
        this.state = !this.state;
        this.callback(this.state);
    }.bind(this));
};

StateButton.prototype.set = function set() {
    this.state = true;
    this.callback(this.state);
};

StateButton.prototype.unset = function unset() {
    this.state = false;
    this.callback(this.state);
};


// this is the toolbar on the right side
var AppControls = (function () {

    var void_switch;
    var node;

    var buildAppControls = function() {
        node = getElemById('app-controls');

        var controls_template = document.getElementById('app-controls-template');
        var contents = document.importNode(controls_template.content, true);
        node.appendChild(contents);
    }


    var initPickingMode = function() {
        var hsv = node.querySelector('#hsv');
        var hsl = node.querySelector('#hsl');

        var active = null;
        active = hsv;
        active.setAttribute('data-active', 'true');

        function switchPickingModeTo(elem) {
            active.removeAttribute('data-active');
            active = elem;
            active.setAttribute('data-active', 'true');
            setVoidSwitch();
            ColorPicker.setPickerMode('picker', active.textContent);
        };


        hsv.addEventListener('click', function() {
            switchPickingModeTo(hsv);
        });
        hsl.addEventListener('click', function() {
            switchPickingModeTo(hsl);
        });
    }


    var initPasteControls = function () {
        node.querySelector('#control-paste-state').addEventListener('click', function() {
            var state = prompt("Enter your state", "0:0/ffffff/1");
            if( state != null ) {
                SampleContainer.pasteContainerState(state);
            }

        });
    }

    var initServerControls = function () {

        var img = document.getElementById('server-image');

        var onServerAnswer = function(data) {
            SampleContainer.pasteContainerState(data['color-string']);
            img.setAttribute('data-image-state','active')
            img.src = 'data:image/png;base64,' + data['image'];
        }


        node.querySelector('#control-connect-server').addEventListener(
            'click', function() {

                img.setAttribute('data-image-state','waiting')
                $.ajax({
                    type: "GET",
                    url: REST_GET_COLOR_STRING,
                    success: onServerAnswer,
                });
            });

        node.querySelector('#control-send-server').addEventListener('click', function() {
            img.setAttribute('data-image-state','waiting')
            $.ajax({
                type: "POST",
                crossDomain: true,
                url: REST_SET_COLOR_STRING,
                success: onServerAnswer,
                data: SampleContainer.getContainerState(),
            });
        });


        node.querySelector('#copy-all').addEventListener('click', function() {
            var s = SampleContainer.getContainerState();
            $('.toast').toast('show');
            // Copy string to clipboard
            navigator.clipboard.writeText(s);

        });


    };

    var initVoidSwitch = function() {
        var void_sample = node.querySelector('#void-sample');
        void_switch = new StateButton(void_sample, function (state) {
            void_sample.setAttribute('data-active', state);
            if (state === true) {
                SampleContainer.unsetActiveSample();
            }
        });
    };

    var unsetVoidSwitch = function() {
        void_switch.unset();
    };

    var setVoidSwitch = function() {
        void_switch.set();
    };

    var initAppControls = function() {

        buildAppControls();
        initPickingMode();
        initPasteControls();
        initServerControls();
        initVoidSwitch();
    };



    return {
        init : initAppControls,
        unsetVoidSample : unsetVoidSwitch,
        setVoidSample : setVoidSwitch,
    };

})();