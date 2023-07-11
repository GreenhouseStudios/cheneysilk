const routes = {
    404: {
        template: "/404.html",
        title: "404",
        description: "Page not found",
    },
    "/": {
        template: "https://storymaps.arcgis.com/collections/bf84e6ebd1c2456a9cdc721779043c01",
        title: "Home",
        description: "This is the home page",
    },
    // storymap: {
    //     template: "https://storymaps.arcgis.com/collections/58b2f050962b4225af36d49a3b63c675",
    //     title: "Storymap Story",
    //     description: "Storymap Story"
    // },
    // "/stories/": {
    //     template: "/404.html",
    //     title: "Storymap Story",
    //     description: "Storymap Story"
    // },
    "/about": {
        template: "/about.html",
        title: "About Us",
        description: "This is the about page",
    },
    "/contact": {
        template: "/contact.html",
        title: "Contact Us",
        description: "This is the contact page",
    },
};


// create document click that watches the nav links only
document.addEventListener("click", (e) => {
    const { target } = e;
    if (!target.matches("a")) {
        return;
    }
    e.preventDefault();
    route();
});


const route = (event) => {
    event = event || window.event; // get window.event if event argument not provided
    event.preventDefault();
    // window.history.pushState(state, unused, target link);
    window.history.pushState({}, "", event.target.href);
    locationHandler();
};

const locationHandler = async () => {
    const location = window.location.pathname; // get the url path
    console.log(location)
    // if the path length is 0, set it to primary page route
    if (location.length == 0) {
        location = "/";
    }
    // get the route object from the urlRoutes object
    const route = routes[location] || routes["404"];

    console.log(route)
    // if(location.startsWith("/stories/")){
    //     route = routes["storymap"]
    // }

    // get the html from the template
    const html = await fetch(route.template).then((response) => response.text());
    // set the content of the content div to the html
    document.getElementById("iframeContainer").innerHTML = html;
    // set the title of the document to the title of the route
    document.title = route.title;
    // set the description of the document to the description of the route
    // document
    //     .querySelector('meta[name="description"]')
    //     .setAttribute("iframeContainer", route.description);
};

// add an event listener to the window that watches for url changes
window.onpopstate = locationHandler;
// call the urlLocationHandler function to handle the initial url
window.route = route;
// call the urlLocationHandler function to handle the initial url
locationHandler();