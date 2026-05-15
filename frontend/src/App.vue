<script setup>
import { ref, onMounted } from "vue";

const view = ref("auth");
const authTab = ref("login");
const user = ref(null);
const files = ref([]);
const loading = ref(false);

const loginForm = ref({ nim: "", password: "" });
const registerForm = ref({ name: "", nim: "", email: "", password: "" });
const selectedFile = ref(null);

const toast = ref({ message: "", type: "" });
let toastTimer = null;

function showToast(message, type = "error") {
    clearTimeout(toastTimer);
    toast.value = { message, type };
    toastTimer = setTimeout(() => (toast.value = { message: "", type: "" }), 3000);
}

onMounted(async () => {
    const res = await fetch("/api/me");
    if (res.ok) {
        user.value = await res.json();
        view.value = "dashboard";
        await fetchFiles();
    }
});

async function login() {
    loading.value = true;
    const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(loginForm.value),
    });
    const data = await res.json();
    loading.value = false;
    if (!res.ok) {
        showToast(data.error);
        return;
    }
    user.value = data;
    view.value = "dashboard";
    await fetchFiles();
}

async function register() {
    loading.value = true;
    const res = await fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registerForm.value),
    });
    const data = await res.json();
    loading.value = false;
    if (!res.ok) {
        showToast(data.error);
        return;
    }
    user.value = data;
    view.value = "dashboard";
    await fetchFiles();
}

async function logout() {
    await fetch("/api/logout", { method: "POST" });
    user.value = null;
    files.value = [];
    view.value = "auth";
}

async function fetchFiles() {
    const res = await fetch("/api/files");
    if (res.ok) files.value = await res.json();
}

async function uploadFile() {
    if (!selectedFile.value) return;
    loading.value = true;
    const form = new FormData();
    form.append("file", selectedFile.value);
    const res = await fetch("/api/files", { method: "POST", body: form });
    loading.value = false;
    if (!res.ok) {
        const d = await res.json();
        showToast(d.error);
        return;
    }
    selectedFile.value = null;
    showToast("File uploaded successfully.", "success");
    await fetchFiles();
}

async function deleteFile(originalName) {
    const res = await fetch(`/api/files/${originalName}`, { method: "DELETE" });
    if (!res.ok) {
        showToast("Failed to delete file.");
        return;
    }
    showToast("File deleted.", "success");
    await fetchFiles();
}

function downloadFile(originalName) {
    window.location.href = `/api/files/${originalName}`;
}

function onFileChange(e) {
    selectedFile.value = e.target.files[0] ?? null;
}
</script>

<template>
    <!-- Toast notification -->
    <div
        v-if="toast.message"
        :style="{
            position: 'fixed',
            top: '16px',
            right: '16px',
            padding: '12px 20px',
            borderRadius: '6px',
            color: 'white',
            fontWeight: 'bold',
            zIndex: 1000,
            background: toast.type === 'success' ? '#16a34a' : '#dc2626',
        }"
    >
        {{ toast.message }}
    </div>

    <!-- Auth View -->
    <div v-if="view === 'auth'">
        <h1>Nusantara Tech</h1>

        <div>
            <button @click="authTab = 'login'">Login</button>
            <button @click="authTab = 'register'">Register</button>
        </div>

        <!-- Login Form -->
        <form v-if="authTab === 'login'" @submit.prevent="login">
            <div>
                <label>NIM</label>
                <input v-model="loginForm.nim" type="text" required />
            </div>
            <div>
                <label>Password</label>
                <input v-model="loginForm.password" type="password" required />
            </div>
            <button type="submit" :disabled="loading">
                {{ loading ? "Logging in..." : "Login" }}
            </button>
        </form>

        <!-- Register Form -->
        <form v-if="authTab === 'register'" @submit.prevent="register">
            <div>
                <label>Full Name</label>
                <input v-model="registerForm.name" type="text" required />
            </div>
            <div>
                <label>NIM</label>
                <input v-model="registerForm.nim" type="text" required />
            </div>
            <div>
                <label>Email</label>
                <input v-model="registerForm.email" type="email" />
            </div>
            <div>
                <label>Password</label>
                <input v-model="registerForm.password" type="password" required />
            </div>
            <button type="submit" :disabled="loading">
                {{ loading ? "Registering..." : "Register" }}
            </button>
        </form>
    </div>

    <!-- Dashboard View -->
    <div v-if="view === 'dashboard'">
        <div>
            <h1>Welcome, {{ user.name }}</h1>
            <p>NIM: {{ user.nim }}</p>
            <p>Email: {{ user.email }}</p>
            <button @click="logout">Logout</button>
        </div>

        <hr />

        <h2>Upload File</h2>
        <form @submit.prevent="uploadFile">
            <input type="file" @change="onFileChange" />
            <button type="submit" :disabled="loading || !selectedFile">
                {{ loading ? "Uploading..." : "Upload" }}
            </button>
        </form>

        <hr />

        <h2>My Files</h2>
        <p v-if="files.length === 0">No files uploaded yet.</p>
        <table v-else>
            <thead>
                <tr>
                    <th>Filename</th>
                    <th>Uploaded At</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="file in files" :key="file.id">
                    <td>{{ file.original_name }}</td>
                    <td>{{ new Date(file.uploaded_at).toLocaleString() }}</td>
                    <td>
                        <button @click="downloadFile(file.original_name)">
                            Download
                        </button>
                        <button @click="deleteFile(file.original_name)">Delete</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
