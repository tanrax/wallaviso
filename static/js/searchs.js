$(function () {
	let appSearchs = new Vue({
		el: '#appSearchs',
		delimiters: ['[[', ']]'],
		data: {
			search: document.querySelector('#form_search input#name').value,
			search_item: '',
			search_send: '',
			results: true,
			confirm_add: false
		},
		methods: {
			next: (search_item) => {
				appSearchs.results = false;
				appSearchs.confirm_add = true;
				appSearchs.search_item = search_item;
				document.querySelector('main').classList.add('col-sm-12');
				document.querySelector('main').classList.remove('col-sm-8');
				window.scrollTo(document.querySelector('main').scrollTop, 0);
			},
			add: (search_send) => {
				appSearchs.search_send = search_send;
				let form_add = document.querySelector('#form_add');
				form_add.name.value = search_send;
				form_add.submit();
			},
			back: () => {
				appSearchs.results = true;
				appSearchs.confirm_add = false;
				document.querySelector('main').classList.remove('col-sm-12');
				document.querySelector('main').classList.add('col-sm-8');

			}
		}
	})
})
