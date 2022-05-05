// This is to fix an error with jinja
let debug = document.getElementById("recipes");
debug.lastChild.replaceWith(...debug.childNodes);

const CATEGORIES = [
	"appetizer",
	"snack",
	"breakfast",
	"salads",
	"main",
	"soup",
	"dessert",
	"beverage",
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

//TODO:
const UpdateButtons = (list) => {
	for (let i of list) {
		id = document.getElementById(i);
		class_ = document.getElementsByClassName(`c_${i}`);
		if (!class_) {
			id.classList.add("visually-hidden");
		} else {
			id.addEventListener("click", function (e) {
				e.preventDefault;
				category(i);
				let cParent = document.getElementsByClassName("c_category");
				for (j of cParent) {
					j.innerText = i;
				}
			});
		}
	}
};

UpdateButtons(CATEGORIES);
all.addEventListener("click", function (e) {
	e.preventDefault;
	category("all");
	let cParent = document.getElementsByClassName("c_category");
	for (i of cParent) {
		i.innerText = "Category";
	}
});
