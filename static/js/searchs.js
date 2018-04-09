(function() {
	let main_el = '#appSearchs'; 
        // Load globals
        var globals = document.querySelector('#globals');
        // Enable devtools Vuejs
        if (globals.dataset.debug) Vue.config.devtools = true;
        // Load VueJS
	if(document.querySelector(main_el) !== null) {
		let appSearchs = new Vue({
			el: main_el,
			delimiters: ['[[', ']]'],
			data: {
                                globals: document.querySelector('#globals'),
				main: document.querySelector('main'),
				form_add: document.querySelector('#form_add'),
				search_select: '',
				results: true,
				confirm_add: false,
				lat: 0,
				lng: 0,
                                listLocations: [],
                                postal_code: '',
                                location: '',
                                name: '',
                                listDistance: Array.from(Array(401).keys()),
                                distance: '10',
                                max_price: '',
                                min_price: '',
                                results: [],
                                loading: false,
                                first_search: true,
                                step: 1
			},
			methods: {
                                searchPostalCode: function() {
                                    let url = globals.dataset.urlapipostalcode + '/api/v1/postal_code/' + appSearchs.postal_code;
                                    this.$http.get(url).then(response => {
                                        // Get data
                                        appSearchs.listLocations = response.body;
                                    }, response => {
                                        // error callback
                                    });
                                },
                                setLocation: function(e) {
                                    let url = globals.dataset.urlapipostalcode + '/api/v1/index/' + e.target.options.selectedIndex;
                                    this.$http.get(url).then(response => {
                                        // Get data
                                        appSearchs.lng = response.body[0]['lat'];
                                        appSearchs.lat = response.body[0]['lng'];
                                    }, response => {
                                        // error callback
                                    });
                                },
                                getSearchs: function() {
                                    appSearchs.loading = true;
                                    appSearchs.first_search = false;
                                    // Clear results
                                    appSearchs.results = [];
                                    // Scroll to top
	                            window.scroll(0, 0);
                                    // Get results
                                    this.$http.post('/api/search', {
                                        kws: appSearchs.name,
                                        dist: appSearchs.distance,
                                        lat: appSearchs.lat,
                                        lng: appSearchs.lng,
                                        maxPrice: appSearchs.max_price,
                                        minPrice: appSearchs.min_price
                                    }).then(response => {
                                        // Get data
                                        appSearchs.loading = false;
                                        appSearchs.results = response.body['items'].splice(0, appSearchs.globals.dataset.limitresults);
                                    }, response => {
                                        // error callback
                                    });
                                },
				next: function (search) {
                                    appSearchs.search_select = search;
                                    appSearchs.step = 2;
                                    // Move scroll to next step
                                    window.scroll(0, 0);
				},
				add: function (name) {
                                    // Add values form search to form add
                                    appSearchs.form_add = document.querySelector('#form_add');
                                    appSearchs.form_add.elements.name.value = name;
                                    // Send form add
                                    appSearchs.form_add.submit();
				},
				back: function () {
                                    appSearchs.step = 1;
				}
			}
		});
	}
})();
