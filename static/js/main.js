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
			input2: 'without-image',
			input3: 'id=ctl00_ctl00_header_ctl00_buildingName',
			input4: 'id=site-body',
			input5: 'class_=col-xs-12',
		}
	}
}

Vue.createApp(VueApp).mount('#app');
