function getElemById(id) {
    return document.getElementById(id);
}

function allowDropEvent(e) {
    e.preventDefault();
}

var SAMPLES_PER_LINE = 5;
var NUM_STARTING_LINES = 4;
var DIGEST_UNIFIER = '/';

LOCAL_SERVER = 'http://127.0.0.1:5000/'
REST_GET_COLOR_STRING = LOCAL_SERVER + 'get-color-string'
REST_SET_COLOR_STRING = LOCAL_SERVER + 'set-color-string'