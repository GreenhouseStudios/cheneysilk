const routes = {
    "/": {
        title: "Home",
        description: "This is the home page",
    },
    storymap: {
        template: "https://storymaps.arcgis.com/stories/660a1cbd115d4681956ddc36924d8b34",
        title: "Storymap Story",
        description: "Storymap Story"
    },
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
    // window.history.pushState({}, "", event.target.href);
    locationHandler();
};

const locationHandler = async () => {
    // console.log(window.location.pathname)
    // let location =  window.location.pathname.replace("/cheneysilk",""); // get the url path
    // console.log(location)
    // // if the path length is 0, set it to primary page route
    // if (location.length == 0) {
    //     location = "/";
    }
    // get the route object from the urlRoutes object
    // let route = routes[location] || routes["404"];
    // let route = routes[location]
    
    // console.log(route)

    // let template = "https://storymaps.arcgis.com/collections/bf84e6ebd1c2456a9cdc721779043c01" ;
    // const fullscreenIframe = document.getElementById('fullscreenIframe');
    // fullscreenIframe.src = template;

    // document.title = route.title;
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