// Creates buttons under the wtf form areas to allow users to dynamically add new content to their form
let initialAddedIngredients = document.getElementById("ingredients").childNodes;
let initialAddedDirections = document.getElementById("directions").childNodes;
let partNumber = initialAddedDirections.length;
let ingredientNumber = initialAddedIngredients.length;

function makeIngredientsPretty() {
	// Add Bootstrap Classes to Ingredients Fields
	let currNumber = 1;
	for (let i of initialAddedIngredients) {
		i.classList.add("form-group");
		i.lastChild.classList.add("form-control");
		i.lastChild.classList.add("my-2");
		i.firstChild.innerText = `Ingredient ${currNumber}:`;
		currNumber++;
	}
}

function makeDirectionsPretty() {
	let currNumber = 1;
	for (let i of initialAddedDirections) {
		// Add Bootstrap Classes to Directions Fields
		i.classList.add("form-group");
		i.lastChild.classList.add("form-control");
		i.lastChild.classList.add("my-2");
		i.lastChild.rows = 3;
		i.firstChild.innerText = `Part ${currNumber}:`;
		currNumber++;
	}
}
function ingredientButton() {
	//create the two buttons. One to add a new field, and one to delete the last field
	let addIngredientButton = document.createElement("button");
	let deleteButton = document.createElement("button");

	addIngredientButton.addEventListener("click", function (e) {
		//create the button to add more inputs for the user
		e.preventDefault();
		ingredientNumber++;
		let allIngredientsWrapper = document.getElementById("ingredients");
		let allIngredientField =
			allIngredientsWrapper.getElementsByTagName("input");
		if (allIngredientField.length > 100) {
			//checks to see if the amount of ingredients are over 100
			ingredientNumber--;
			return;
		}
		//creates the new li's
		let ingredientInputIds = [];
		for (let i = 0; i < allIngredientField.length; i++) {
			ingredientInputIds.push(
				parseInt(allIngredientField[i].name.split("-")[1])
			);
		}
		let newFieldName = `ingredients-${Math.max(...ingredientInputIds) + 1}`;
		allIngredientsWrapper.insertAdjacentHTML(
			"beforeend",
			`
        <li><label for="${newFieldName}">Ingredient ${ingredientNumber}:</label> <input id="${newFieldName}" name="${newFieldName}" type="text" value="" class="form-control my-2"></li> 
        `
		);
	});

	deleteButton.addEventListener("click", function (e) {
		//create the delete button next to the add button which will remove the last row added
		e.preventDefault();
		ingredientNumber--;
		lastIngredientField = document
			.getElementById("ingredients")
			.lastChild.remove();
	});

	// Create the buttons and  manipulate the DOM
	addIngredientButton.classList.add("btn");
	addIngredientButton.classList.add("btn-secondary");
	addIngredientButton.classList.add("my-2");
	addIngredientButton.classList.add("mx-2");
	addIngredientButton.innerText = "Add Ingredient";
	let ingredientsSection = document.getElementById("ingredients").parentElement;
	deleteButton.classList.add("btn");
	deleteButton.classList.add("btn-danger");
	deleteButton.classList.add("my-2");
	deleteButton.innerText = "Delete";
	// Styles the first element to make it show up correctly
	let ingredientsStyle =
		document.getElementById("ingredients").firstChild.lastChild;
	ingredientsStyle.classList.add("form-control");
	ingredientsStyle.classList.add("my-2");
	ingredientsSection.appendChild(addIngredientButton);
	ingredientsSection.appendChild(deleteButton);
}

function directionsButton() {
	//Basically a copy of ingredientsButton. The main difference is that directions is a
	//text area field because instructions require a lot typing then ingredients
	let addDirectionButton = document.createElement("button");
	let deleteButton = document.createElement("button");

	addDirectionButton.addEventListener("click", function (e) {
		//create the button to add more inputs for the user
		e.preventDefault();
		partNumber++;
		let allDirectionsWrapper = document.getElementById("directions");
		let allDirectionField = allDirectionsWrapper.getElementsByTagName("input");
		if (allDirectionField.length > 100) {
			//checks to see if there are more then 100 as that is my limit
			partNumber--;
			return;
		}
		let newFieldName = `directions-${partNumber - 1}`;
		allDirectionsWrapper.insertAdjacentHTML(
			"beforeend",
			`
        <li class="form-group"><label for="${newFieldName}"> Part ${partNumber}: </label> <textarea id="${newFieldName}" name="${newFieldName}" type="text" value="" rows="3" class="form-control my-2"></textarea> 
        `
		);
	});

	deleteButton.addEventListener("click", function (e) {
		//create the delete button next to the add button which will remove the last row added
		e.preventDefault();
		partNumber--;
		lastDirectionField = document
			.getElementById("directions")
			.lastChild.remove();
	});

	// Create the buttons and  manipulate the DOM
	addDirectionButton.classList.add("btn");
	addDirectionButton.classList.add("btn-secondary");
	addDirectionButton.classList.add("my-2");
	addDirectionButton.classList.add("mx-2");
	addDirectionButton.innerText = "Add Direction";
	deleteButton.classList.add("btn");
	deleteButton.classList.add("btn-danger");
	deleteButton.classList.add("my-2");
	deleteButton.innerText = "Delete";
	// Styles the first element to make it show up correctly
	let directionsSection = document.getElementById("directions").parentElement;
	let directionsStyle =
		document.getElementById("directions").firstChild.lastChild;
	directionsStyle.classList.add("form-control");
	directionsStyle.classList.add("my-2");
	directionsSection.appendChild(addDirectionButton);
	directionsSection.appendChild(deleteButton);
}

//run the functions to change the DOM
ingredientButton();
directionsButton();
makeIngredientsPretty();
makeDirectionsPretty();
