// This is to fix an error with jinja
let debug = document.getElementById("recipes").lastChild;
debug.replaceWith(...debug.childNodes);

//Create the categories buttons
let appetizer = document.getElementById("appetizer");
let snacks = document.getElementById("snack");
let breakfast = document.getElementById("breakfast");
let salads = document.getElementById("salads");
let main = document.getElementById("main");
let soup = document.getElementById("soup");
let dessert = document.getElementById("dessert");
let beverages = document.getElementById("beverage");
let all = document.getElementById("all");

let allRecipes = document.getElementById("recipes").children;

let category = (type) => {
	for (let i of allRecipes) {
		if (type == "all") {
			i.classList.remove("visually-hidden");
			continue;
		}
		if (i.classList.contains(`c_${type}`)) {
			i.classList.remove("visually-hidden");
		} else {
			i.classList.add("visually-hidden");
		}
	}
};

appetizer.addEventListener("click", function (e) {
	e.preventDefault;
	category("appetizer");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Appetizers";
	}
});
snacks.addEventListener("click", function (e) {
	e.preventDefault;
	category("snacks");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Snacks";
	}
});
breakfast.addEventListener("click", function (e) {
	e.preventDefault;
	category("breakfast");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Breakfasts";
	}
});
salads.addEventListener("click", function (e) {
	e.preventDefault;
	category("salads");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Salads";
	}
});
main.addEventListener("click", function (e) {
	e.preventDefault;
	category("main");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Main Dishes";
	}
});
soup.addEventListener("click", function (e) {
	e.preventDefault;
	category("soup");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Soups";
	}
});
dessert.addEventListener("click", function (e) {
	e.preventDefault;
	category("dessert");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Desserts";
	}
});
beverages.addEventListener("click", function (e) {
	e.preventDefault;
	category("beverages");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Beverages";
	}
});

all.addEventListener("click", function (e) {
	e.preventDefault;
	category("all");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Category";
	}
});
