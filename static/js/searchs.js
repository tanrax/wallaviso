(function() {
	let main_el = '#appSearchs'; 
	if(document.querySelector(main_el) !== null) {
		let appSearchs = new Vue({
			el: main_el,
			delimiters: ['[[', ']]'],
			data: {
				form_search: document.querySelector('#form_search'),
				search: document.querySelector('#form_search input#name').value,
				main: document.querySelector('main'),
				form_add: document.querySelector('#form_add'),
				search_item: '',
				search_send: '',
				results: true,
				confirm_add: false,
				lat: 0,
				lng: 0
			},
			methods: {
				mounted: () => {
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
		appSearchs.mounted();
	}
})();
