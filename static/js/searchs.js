(function() {
	let main_el = '#appSearchs'; 
        Vue.config.devtools = true
	if(document.querySelector(main_el) !== null) {
		let appSearchs = new Vue({
			el: main_el,
			delimiters: ['[[', ']]'],
			data: {
                                globals: document.querySelector('#globals'),
				main: document.querySelector('main'),
				form_add: document.querySelector('#form_add'),
				search_item: '',
				search_send: '',
				results: true,
				confirm_add: false,
				lat: 0,
				lng: 0,
                                listLocations: [],
                                postal_code: '',
                                location: '',
                                name: '',
                                listDistance: [
                                    { key: '0_1000', value: 'Muy cerca (1km)'},
                                    { key: '0_5000', value: 'En mi zona (5km)'},
                                    { key: '0_10000', value: 'En mi ciudad (10km)'},
                                    { key: '0_', value: 'Sin límite'}
                                ],
                                distance: '0_',
                                max_price: '',
                                min_price: ''
			},
			methods: {
                                searchPostalCode: function() {
                                    let url = appSearchs.globals.dataset.urlapipostalcode + '/api/v1/postal_code/' + appSearchs.postal_code;
                                    this.$http.get(url).then(response => {
                                        // Get data
                                        appSearchs.listLocations = response.body;
                                    }, response => {
                                        // error callback
                                    });
                                },
                                setLocation: function(e) {
                                    let url = appSearchs.globals.dataset.urlapipostalcode + '/api/v1/index/' + e.target.options.selectedIndex;
                                    this.$http.get(url).then(response => {
                                        // Get data
                                        appSearchs.lat = response.body[0]['lat'];
                                        appSearchs.lng = response.body[0]['lng'];
                                    }, response => {
                                        // error callback
                                    });
                                },
				next: (search_item) => {
					appSearchs.results = false;
					appSearchs.confirm_add = true;
					appSearchs.search_item = search_item;
					// Adjust columns
					appSearchs.main = document.querySelector('main');
					appSearchs.main.classList.add('col-sm-12');
					appSearchs.main.classList.remove('col-sm-8');
					// Move scroll to next step
					window.scrollTo(appSearchs.main.scrollTop, 0);
				},
				add: (search_send) => {
					// Add values form search to form add
					appSearchs.form_add = document.querySelector('#form_add');
					appSearchs.form_add.elements.distance.value =  appSearchs.form_search.elements.distance.value;
					appSearchs.form_add.elements.max_price.value =  appSearchs.form_search.elements.max_price.value;
					appSearchs.search_send = search_send;
					appSearchs.form_add.elements.add.value = search_send;
					// Send form add
					appSearchs.form_add.submit();
				},
				back: () => {
					appSearchs.results = true;
					appSearchs.confirm_add = false;
					appSearchs.main.classList.remove('col-sm-12');
					appSearchs.main.classList.add('col-sm-8');
				}
			}
		});
	}
})();
