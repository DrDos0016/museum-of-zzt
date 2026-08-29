{
    // Museum of ZZT Zeta Configuration
    // Using {{meta.zeta_config.fallback|yesno:'FALLBACK,Predefined' }} Config: [{{meta.zeta_config.pk}}] {{meta.zeta_config.name}}
    // Executable: {{meta.executable}}
    // Charset   : {{meta.charset}}
    // Blinking  : {{meta.blinking}}
    {% if path %}path: "{{path}}",{% endif %}
    {% if arg %}arg: "{{arg}}",{% endif %}
    {% if commands %}commands: {{commands|safe}},{% endif %}
    {% if storage %}storage: {
        {% if storage.type %}type: "{{storage.type}}",{% endif %}
        {% if storage.database %}database: "{{storage.database}}", // [{{meta.save_storage_key}}]{% endif %}
    },{% endif %}
    {% if engine %}engine: {
        {% if engine.charset %}charset: '{{engine.charset|safe}}',{% endif %}
        {% if engine.lock_charset %}lock_charset: {{engine.lock_charset}},{% endif %}
        {% if engine.palette %}palette: {{engine.palette}},{% endif %}
        {% if engine.lock_palette %}lock_palette: {{engine.lock_palette}},{% endif %}
        {% if engine.memory_limit %}memory_limit: {{engine.memory_limit}},{% endif %}
        {% if engine.extended_memory_limit %}extended_memory_limit: {{engine.extended_memory_limit}},{% endif %}
        {% if engine.skip_kc %}skip_kc: {{engine.skip_kc}},{% endif %}
    },{% endif %}
    {% if render %}render: {
        {% if render.canvas %}canvas: document.querySelector("{{render.canvas}}"),{% endif %}
        {% if render.type %}type: "{{render.type}}",{% endif %}
        {% if render.blink_cycle_duration %}blink_cycle_duration: {{render.blink_cycle_duration}},{% endif %}
        {% if render.charset_override %}charset_override: "",{% endif %}
        {% if render.style %}style: "2002",{% endif %}
    },{% endif %}
    {% if audio %}audio: {
        {% if audio.buffer_size %}bufferSize: "???",{% endif %}
        {% if audio.sample_rate %}sampleRate: "???",{% endif %}
        {% if audio.note_delay %}noteDelay: 1,{% endif %}
        {% if audio.volume %}volume: 0.2,{% endif %}
    },{% endif %}
    {% if files %}files: [
        {% for file in files %}{{file|safe}},
        {% endfor %}{% if engine.external_charset %}{'type': 'file', 'url': '/static/data/zeta_chr/{{engine.charset}}', 'filename': '{{engine.charset}}'},{% endif %}
    ],
    {% endif %}
}
