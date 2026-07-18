// Fix DEF-002 (S4502): reenvia el token CSRF en cada peticion mutante.
// Envuelve window.fetch para agregar la cabecera X-CSRFToken leida de la
// cookie 'csrf_token' en peticiones same-origin que no sean seguras.
(function () {
    function getCookie(name) {
        const match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return match ? decodeURIComponent(match.pop()) : '';
    }

    const SAFE = /^(GET|HEAD|OPTIONS|TRACE)$/i;
    const originalFetch = window.fetch.bind(window);

    window.fetch = function (input, init) {
        init = init || {};
        const method = (init.method || (typeof input !== 'string' && input.method) || 'GET');

        // Solo same-origin: si input es URL absoluta a otro origen, no tocar.
        let sameOrigin = true;
        try {
            const url = new URL((typeof input === 'string' ? input : input.url), window.location.href);
            sameOrigin = url.origin === window.location.origin;
        } catch (e) { /* URL relativa -> same-origin */ }

        if (!SAFE.test(method) && sameOrigin) {
            const token = getCookie('csrf_token');
            const headers = new Headers(init.headers || (typeof input !== 'string' && input.headers) || {});
            if (token && !headers.has('X-CSRFToken')) {
                headers.set('X-CSRFToken', token);
            }
            init.headers = headers;
        }
        return originalFetch(input, init);
    };
})();
