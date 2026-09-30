async function api(url, options = {}) {
    const isFormData = options.body instanceof FormData;

    const headers = {
        ...(isFormData
            ? {}
            : {
                "Content-Type": "application/json"
            }),
        ...(options.headers || {})
    };

    const response = await fetch(url, {
        credentials: "include",
        ...options,
        headers
    });

    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        throw new Error(
            data.detail || "Request failed"
        );
    }

    return data;
}


function formObject(form) {
    const data = {};

    new FormData(form).forEach((value, key) => {

        if (
            key === "rooms" ||
            key === "priorities"
        ) {
            data[key] = String(value)
                .split(",")
                .map(item => item.trim())
                .filter(Boolean);

        } else {
            data[key] = value;
        }
    });

    return data;
}


function bindAuthForm(
    formId,
    url,
    nextUrl
) {
    const form = document.getElementById(
        formId
    );

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async event => {

            event.preventDefault();

            const message =
                document.getElementById(
                    "message"
                );

            message.textContent = "";
            message.className =
                "message";

            try {

                await api(
                    url,
                    {
                        method: "POST",
                        body: JSON.stringify(
                            formObject(form)
                        )
                    }
                );

                window.location.href =
                    nextUrl;

            } catch (error) {

                message.textContent =
                    error.message;

                message.className =
                    "message error";
            }
        }
    );
}


async function refreshNav() {

    try {

        await api(
            "/api/auth/session-info"
        );

        document
            .getElementById("loginLink")
            ?.classList.add("hidden");

        document
            .getElementById("registerLink")
            ?.classList.add("hidden");

        document
            .getElementById("logoutBtn")
            ?.classList.remove("hidden");

    } catch {
        // User is not logged in.
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        refreshNav();

        document
            .getElementById("logoutBtn")
            ?.addEventListener(
                "click",
                async () => {

                    try {
                        await api(
                            "/api/auth/logout",
                            {
                                method: "POST"
                            }
                        );
                    } finally {
                        window.location.href =
                            "/";
                    }
                }
            );
    }
);