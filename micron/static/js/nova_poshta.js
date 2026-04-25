document.addEventListener('DOMContentLoaded', function () {
    const elements = {
        region: document.getElementById("regionSelect"),
        city: {
            input: document.getElementById("cityInput"),
            results: document.getElementById("citySearchResults"),
            toggle: document.getElementById("toggleCitySelect"),
            ref: document.getElementById("cityRef")
        },
        office: document.getElementById("officeSelect"),
        hiddenRegion: document.getElementById("id_region_hidden"),
        hiddenCity: document.getElementById("id_city_hidden"),
        hiddenPostOffice: document.getElementById("id_post_office_hidden"),
        form: document.getElementById("checkoutForm")
    };

    const API_KEY = typeof NOVA_POSHTA_API_KEY !== 'undefined' && NOVA_POSHTA_API_KEY ? NOVA_POSHTA_API_KEY : "3506f7c429e7bd9d4bd22481c0458455"; // fallback to default or user provided
    const DEFAULT_OPTIONS = {
        loading: '<option value="">Loading...</option>',
        select: '<option value="">Select branch</option>'
    };

    class NovaPoshtaApi {
        constructor(apiKey) {
            this.apiKey = apiKey;
            this.baseUrl = "https://api.novaposhta.ua/v2.0/json/";
        }

        async request(modelName, calledMethod, methodProperties = {}) {
            try {
                const response = await fetch(this.baseUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        apiKey: this.apiKey,
                        modelName,
                        calledMethod,
                        methodProperties
                    })
                });
                const data = await response.json();
                if (!data.success) throw new Error(data.errors?.join(' ') || "API request failed");
                return data;
            } catch (error) {
                console.error(`${modelName}/${calledMethod} failed:`, error);
                throw error;
            }
        }
    }

    const api = new NovaPoshtaApi(API_KEY);
    let citiesData = [];

    const utils = {
        setLoading: (isLoading) => {
            elements.city.input.disabled = isLoading;
            elements.city.toggle.disabled = isLoading;
            elements.city.input.placeholder = isLoading ?
                'Loading...' :
                'Enter city name or choose from list';
        },

        sortByLocale: (a, b, field = 'Description') =>
            a[field].localeCompare(b[field], 'uk'),

        getCityName: (city) => city.Description.split(',')[0].trim().toLowerCase()
    };

    function selectCity(city) {
        elements.city.input.value = city.Description;
        elements.city.ref.value = city.Ref;
        elements.hiddenCity.value = city.Description;
        elements.city.results.style.display = 'none';
        loadOffices(city.Ref);
    }

    let isInitializing = true;

    async function loadRegions() {
        try {
            elements.region.innerHTML = DEFAULT_OPTIONS.loading;
            utils.setLoading(true);
            elements.office.innerHTML = DEFAULT_OPTIONS.select;

            const response = await api.request("Address", "getAreas");
            const filteredAreas = response.data
                .filter(area => area.Description !== 'АРК')
                .sort(utils.sortByLocale);

            elements.region.innerHTML = '<option value="">Select region</option>' +
                filteredAreas.map(area =>
                    `<option value="${area.Ref}">${area.Description}</option>`
                ).join('');

            if (isInitializing && elements.hiddenRegion.value) {
                const activeArea = filteredAreas.find(a => a.Description === elements.hiddenRegion.value);
                if (activeArea) {
                    elements.region.value = activeArea.Ref;
                    await loadCities(activeArea.Ref, true);
                } else {
                    isInitializing = false;
                }
            } else {
                isInitializing = false;
            }

        } catch (error) {
            elements.region.innerHTML = '<option value="">Error loading</option>';
            isInitializing = false;
        }
    }

    async function loadCities(regionRef, fromInit = false) {
        try {
            utils.setLoading(true);
            elements.office.innerHTML = DEFAULT_OPTIONS.select;

            const response = await api.request("Address", "getCities", { AreaRef: regionRef });
            citiesData = response.data.sort(utils.sortByLocale);
            utils.setLoading(false);

            if (fromInit && elements.hiddenCity.value) {
                const activeCity = citiesData.find(c => c.Description === elements.hiddenCity.value);
                if (activeCity) {
                    elements.city.input.value = activeCity.Description;
                    elements.city.ref.value = activeCity.Ref;
                    await loadOffices(activeCity.Ref, true);
                } else {
                    isInitializing = false;
                }
            }

        } catch (error) {
            utils.setLoading(true);
            elements.city.input.placeholder = 'Error loading';
            isInitializing = false;
        }
    }

    function filterCities(searchText) {
        if (!searchText) {
            displaySearchResults(citiesData);
            return;
        }

        const search = searchText.toLowerCase().trim();
        const filtered = citiesData
            .filter(city => utils.getCityName(city).startsWith(search))
            .sort((a, b) => {
                const nameA = utils.getCityName(a);
                const nameB = utils.getCityName(b);
                const aStarts = nameA.startsWith(search);
                const bStarts = nameB.startsWith(search);

                return aStarts === bStarts ?
                    nameA.localeCompare(nameB, 'uk') :
                    bStarts ? 1 : -1;
            });

        displaySearchResults(filtered);
    }

    function displaySearchResults(cities) {
        elements.city.results.innerHTML = '';

        if (cities.length) {
            cities.forEach(city => {
                const div = document.createElement('div');
                div.textContent = city.Description;
                div.onclick = () => selectCity(city);
                elements.city.results.appendChild(div);
            });
            elements.city.results.style.display = 'block';
        } else {
            elements.city.results.style.display = 'none';
        }
    }

    async function loadOffices(cityRef, fromInit = false) {
        try {
            elements.office.innerHTML = DEFAULT_OPTIONS.loading;

            const response = await api.request("Address", "getWarehouses", { CityRef: cityRef });
            const sortedOffices = response.data.sort((a, b) =>
                parseInt(a.Number) - parseInt(b.Number)
            );

            elements.office.innerHTML = DEFAULT_OPTIONS.select +
                sortedOffices.map(office =>
                    `<option value="${office.Ref}">${office.Description}</option>`
                ).join('');

            if (fromInit && elements.hiddenPostOffice.value) {
                const activeOption = Array.from(elements.office.options).find(opt => opt.text === elements.hiddenPostOffice.value);
                if (activeOption) {
                    elements.office.value = activeOption.value;
                }
                isInitializing = false;
            }

        } catch (error) {
            elements.office.innerHTML = '<option value="">Error loading</option>';
            isInitializing = false;
        }
    }

    elements.region.addEventListener("change", (e) => {
        const regionRef = e.target.value;
        if (!isInitializing || e.isTrusted) {
            elements.city.input.value = '';
            elements.hiddenCity.value = '';
            elements.hiddenPostOffice.value = '';
        }

        const activeOption = e.target.options[e.target.selectedIndex];
        if (activeOption && activeOption.value) {
            elements.hiddenRegion.value = activeOption.text;
        } else {
            elements.hiddenRegion.value = "";
        }

        if (regionRef) {
            loadCities(regionRef);
        } else {
            utils.setLoading(true);
            elements.office.innerHTML = DEFAULT_OPTIONS.select;
        }
    });

    elements.city.input.addEventListener('input', (e) => {
        filterCities(e.target.value);
        elements.hiddenCity.value = e.target.value;
    });

    elements.city.input.addEventListener('focus', () => {
        if (!elements.city.input.value) displaySearchResults(citiesData);
    });

    elements.city.toggle.addEventListener('click', () => {
        const isVisible = elements.city.results.style.display === 'block';
        if (isVisible) {
            elements.city.results.style.display = 'none';
        } else {
            displaySearchResults(citiesData);
        }
    });

    document.addEventListener('click', (e) => {
        const isClickInside = [
            elements.city.input,
            elements.city.results,
            elements.city.toggle
        ].some(el => el.contains(e.target));

        if (!isClickInside) {
            elements.city.results.style.display = 'none';
        }
    });

    elements.office.addEventListener("change", (e) => {
        const activeOption = e.target.options[e.target.selectedIndex];
        if (activeOption && activeOption.value) {
            elements.hiddenPostOffice.value = activeOption.text;
        } else {
            elements.hiddenPostOffice.value = "";
        }
    });

    if (elements.form) {
        elements.form.addEventListener("submit", function (e) {
            if (!elements.hiddenRegion.value || !elements.hiddenCity.value || !elements.hiddenPostOffice.value) {
                e.preventDefault();
                alert("Please select a region, city and Nova Poshta branch!");
            }
        });
    }

    loadRegions();
});
