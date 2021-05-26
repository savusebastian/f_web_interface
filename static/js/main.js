$(document).ready(function(){
	$('button').on('click', function(){
		$('.side-nav, .main-content, .side-content').hide();
		$('.loading-element').show();
	});
});


const VueApp = {
	delimiters: ['${', '}'],
	data() {
		return {
			searchInput: '',
			classInput: '',
			classInput2: '',
			input1: '',
			input2: 'district,',
			input3: '',
			input4: '',
			input6: '',
			input7: '',
			input8: '',
		}
	}
}

Vue.createApp(VueApp).mount('#app');
