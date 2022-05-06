// This is to fix an error with jinja
let debug = document.getElementById("recipes");
debug.lastChild.replaceWith(...debug.childNodes);

//shows the category ID and then the NAME
const CATEGORIES = [
	["appetizer", "Appetizers"],
	["snack", "Snacks"],
	["breakfast", "Breakfast"],
	["salads", "Salads"],
	["main", "Main Dishes"],
	["soup", "Soups"],
	["dessert", "Desserts"],
	["beverage", "Beverages"],
];

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

//create the category function
const category = (type) => {
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

//create the buttons function
const UpdateButtons = (list) => {
	for (let i of list) {
		id = document.getElementById(i[0]);
		class_ = document.getElementsByClassName(`c_${i[0]}`);
		if (class_.length < 1) {
			id.classList.add("visually-hidden");
		} else {
			id.addEventListener("click", function (e) {
				e.preventDefault;
				category(i[0]);
				let cParent = document.getElementsByClassName("c_category");
				for (j of cParent) {
					j.innerText = i[1];
				}
			});
		}
	}
};

//run all the functions on start
UpdateButtons(CATEGORIES);
all.addEventListener("click", function (e) {
	e.preventDefault;
	category("all");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Category";
	}
});
