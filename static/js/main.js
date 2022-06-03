function main() {
	const main = document.querySelector('main');
	const form = document.querySelector('form');
	const side_nav = document.querySelector('.side-nav');
	const main_content = document.querySelector('.main-content');
	const side_content = document.querySelector('.side-content');
	const loading_element = document.querySelector('.loading-element');

	if(form) {
		form.addEventListener('submit', function() {
			main.classList.add('center');
			side_nav.classList.add('hidden');
			main_content.classList.add('hidden');
			loading_element.classList.remove('hidden');

			if(side_content) {
				side_content.classList.add('hidden');
			}
		});
	}
}

main();
