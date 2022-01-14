function main() {
	const form = document.querySelector('form');
	const side_nav = document.querySelector('.side-nav');
	const main_content = document.querySelector('.main-content');
	const side_content = document.querySelector('.side-content');
	const loading_element = document.querySelector('.loading-element');

	if(form) {
		form.addEventListener('submit', function(){
			side_nav.style.display = 'none';
			main_content.style.display = 'none';
			loading_element.style.display = 'block';

			if(side_content) {
				side_content.style.display = 'none';
			}
		});
	}
}

main();
