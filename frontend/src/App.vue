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
    if (!res.ok) { showToast(data.error); return; }
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
    if (!res.ok) { showToast(data.error); return; }
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
    if (!res.ok) { const d = await res.json(); showToast(d.error); return; }
    selectedFile.value = null;
    showToast("File uploaded successfully.", "success");
    await fetchFiles();
}

async function deleteFile(originalName) {
    const res = await fetch(`/api/files/${originalName}`, { method: "DELETE" });
    if (!res.ok) { showToast("Failed to delete file."); return; }
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
    <!-- Toast -->
    <div
        v-if="toast.message"
        class="fixed top-4 right-4 z-50 px-4 py-3 rounded text-white text-sm font-medium shadow-lg"
        :class="toast.type === 'success' ? 'bg-green-600' : 'bg-red-600'"
    >
        {{ toast.message }}
    </div>

    <!-- Auth View -->
    <div v-if="view === 'auth'" class="min-h-screen bg-gray-100 flex items-center justify-center">
        <div class="bg-white rounded-lg shadow p-8 w-full max-w-sm">
            <h1 class="text-2xl font-bold text-center text-gray-800 mb-6">Nusantara Tech</h1>

            <!-- Tabs -->
            <div class="flex mb-6 border-b">
                <button
                    @click="authTab = 'login'"
                    class="flex-1 py-2 text-sm font-medium"
                    :class="authTab === 'login' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'"
                >
                    Login
                </button>
                <button
                    @click="authTab = 'register'"
                    class="flex-1 py-2 text-sm font-medium"
                    :class="authTab === 'register' ? 'border-b-2 border-blue-600 text-blue-600' : 'text-gray-500'"
                >
                    Register
                </button>
            </div>

            <!-- Login Form -->
            <form v-if="authTab === 'login'" @submit.prevent="login" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">NIM</label>
                    <input
                        v-model="loginForm.nim"
                        type="text"
                        required
                        class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                    <input
                        v-model="loginForm.password"
                        type="password"
                        required
                        class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <button
                    type="submit"
                    :disabled="loading"
                    class="w-full bg-blue-600 text-white py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
                >
                    {{ loading ? "Logging in..." : "Login" }}
                </button>
            </form>

            <!-- Register Form -->
            <form v-if="authTab === 'register'" @submit.prevent="register" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                    <input
                        v-model="registerForm.name"
                        type="text"
                        required
                        class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">NIM</label>
                    <input
                        v-model="registerForm.nim"
                        type="text"
                        required
                        class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input
                        v-model="registerForm.email"
                        type="text"
                        class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
                    <input
                        v-model="registerForm.password"
                        type="password"
                        required
                        class="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                </div>
                <button
                    type="submit"
                    :disabled="loading"
                    class="w-full bg-blue-600 text-white py-2 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
                >
                    {{ loading ? "Registering..." : "Register" }}
                </button>
            </form>
        </div>
    </div>

    <!-- Dashboard View -->
    <div v-if="view === 'dashboard'" class="min-h-screen bg-gray-100">
        <!-- Header -->
        <div class="bg-white shadow px-6 py-4 flex items-center justify-between">
            <div>
                <h1 class="text-lg font-bold text-gray-800">Welcome, {{ user.name }}</h1>
                <p class="text-sm text-gray-500">NIM: {{ user.nim }} · {{ user.email }}</p>
            </div>
            <button
                @click="logout"
                class="text-sm text-gray-500 hover:text-red-600 font-medium"
            >
                Logout
            </button>
        </div>

        <div class="max-w-3xl mx-auto px-4 py-8 space-y-8">
            <!-- Upload -->
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-base font-semibold text-gray-700 mb-4">Upload File</h2>
                <form @submit.prevent="uploadFile" class="flex items-center gap-3">
                    <input
                        type="file"
                        @change="onFileChange"
                        class="text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-sm file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200"
                    />
                    <button
                        type="submit"
                        :disabled="loading || !selectedFile"
                        class="bg-blue-600 text-white px-4 py-1.5 rounded text-sm font-medium hover:bg-blue-700 disabled:opacity-50 whitespace-nowrap"
                    >
                        {{ loading ? "Uploading..." : "Upload" }}
                    </button>
                </form>
            </div>

            <!-- File List -->
            <div class="bg-white rounded-lg shadow p-6">
                <h2 class="text-base font-semibold text-gray-700 mb-4">My Files</h2>
                <p v-if="files.length === 0" class="text-sm text-gray-400">No files uploaded yet.</p>
                <table v-else class="w-full text-sm">
                    <thead>
                        <tr class="text-left text-gray-500 border-b">
                            <th class="pb-2 font-medium">Filename</th>
                            <th class="pb-2 font-medium">Uploaded At</th>
                            <th class="pb-2 font-medium text-right">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr
                            v-for="file in files"
                            :key="file.id"
                            class="border-b last:border-0 hover:bg-gray-50"
                        >
                            <td class="py-3 text-gray-800">{{ file.original_name }}</td>
                            <td class="py-3 text-gray-500">{{ new Date(file.uploaded_at).toLocaleString() }}</td>
                            <td class="py-3 text-right space-x-2">
                                <button
                                    @click="downloadFile(file.original_name)"
                                    class="text-blue-600 hover:underline text-sm"
                                >
                                    Download
                                </button>
                                <button
                                    @click="deleteFile(file.original_name)"
                                    class="text-red-500 hover:underline text-sm"
                                >
                                    Delete
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</template>
