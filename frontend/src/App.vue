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
const uploadView = ref(false);
const isDragging = ref(false);

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
    uploadView.value = false;
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
        if (res.status === 413) {
            showToast("File is too large to be uploaded.", "error");
            return;
        }
        try {
            const d = await res.json();
            showToast(d.error || "Upload failed", "error");
        } catch (e) {
            showToast(`Server error: ${res.statusText}`, "error");
        }
        return;
    }
    selectedFile.value = null;
    showToast("File uploaded successfully.", "success");
    uploadView.value = false;
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

function handleFileSelection(file) {
    if (!file) {
        selectedFile.value = null;
        return;
    }
    if (!isImage(file.name)) {
        showToast("Only image files are allowed to be uploaded.", "error");
        selectedFile.value = null;
        return;
    }
    if (file.size > 1 * 1024 * 1024) {
        showToast("File is too large. Maximum size is 1MB.", "error");
        selectedFile.value = null;
        return;
    }
    selectedFile.value = file;
}

function onFileChange(e) {
    handleFileSelection(e.target.files[0] ?? null);
    if (e.target) e.target.value = '';
}

function onDragOver(e) {
    e.preventDefault();
    isDragging.value = true;
}

function onDragLeave(e) {
    e.preventDefault();
    isDragging.value = false;
}

function onDrop(e) {
    e.preventDefault();
    isDragging.value = false;
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
    }
}

function formatDate(dateStr) {
    // Pastikan format tanggal memiliki info zona waktu (UTC) agar tidak dianggap sebagai waktu lokal
    if (dateStr && !dateStr.endsWith('Z') && !dateStr.includes('+')) {
        dateStr = dateStr.replace(' ', 'T') + 'Z';
    }
    const d = new Date(dateStr);
    const now = new Date();
    const diff = Math.floor((now - d) / 1000);
    if (diff < 60) return "Just now";
    if (diff < 3600) return `${Math.floor(diff / 60)} minutes ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    if (diff < 604800) return `${Math.floor(diff / 86400)} days ago`;
    return d.toLocaleDateString();
}

function getFileExt(name) {
    return name.split('.').pop()?.toUpperCase() || 'FILE';
}

function isImage(name) {
    return /\.(png|jpg|jpeg|gif|webp|svg|bmp)$/i.test(name);
}

function getObjectUrl(file) {
    return URL.createObjectURL(file);
}
</script>

<template>
    <!-- Toast Notification -->
    <div v-if="toast.message"
        class="fixed top-4 right-4 z-50 px-5 py-3 rounded-lg text-white text-sm font-medium shadow-lg flex items-center gap-2 transition-all duration-300"
        :class="toast.type === 'success' ? 'bg-secondary' : 'bg-error-red'">
        <span class="material-symbols-outlined" style="font-size:16px;">
            {{ toast.type === 'success' ? 'check_circle' : 'error' }}
        </span>
        {{ toast.message }}
    </div>

    <!-- ===================== AUTH VIEW ===================== -->
    <div v-if="view === 'auth'"
        class="min-h-screen bg-surface-container-high flex items-center justify-center p-4 md:p-10">

        <!-- LOGIN TAB -->
        <div v-if="authTab === 'login'"
            class="w-full max-w-md bg-canvas-white rounded-lg border border-hairline p-6 md:p-8">
            <!-- Logo -->
            <div class="text-center mb-8">
                <h1 class="font-display-product text-3xl font-bold text-primary tracking-tight mb-1">ADSIS</h1>
                <p class="font-mono text-label-mono uppercase text-slate tracking-widest text-xs">Nusantara Tech</p>
            </div>

            <!-- Login Form -->
            <form @submit.prevent="login" class="flex flex-col gap-6">
                <div class="flex flex-col gap-2">
                    <label class="font-mono text-label-mono uppercase text-on-surface text-xs tracking-widest"
                        for="login-nim">NIM</label>
                    <input v-model="loginForm.nim" id="login-nim" type="text" required placeholder="Enter your NIM"
                        class="input-field" />
                </div>
                <div class="flex flex-col gap-2">
                    <label class="font-mono text-label-mono uppercase text-on-surface text-xs tracking-widest"
                        for="login-password">Password</label>
                    <input v-model="loginForm.password" id="login-password" type="password" required
                        placeholder="Enter your password" class="input-field" />
                </div>
                <button type="submit" :disabled="loading" class="btn-primary w-full mt-1">
                    <span v-if="loading" class="material-symbols-outlined animate-spin"
                        style="font-size:16px;">progress_activity</span>
                    {{ loading ? "Accessing..." : "Access System" }}
                </button>
            </form>

            <!-- Switch to Register -->
            <div class="mt-6 text-center border-t border-hairline pt-6">
                <p class="text-slate text-sm">
                    Need an account?
                    <button @click="authTab = 'register'"
                        class="text-ink hover:text-action-blue underline transition-colors ml-1">Register here</button>
                </p>
            </div>
        </div>

        <!-- REGISTER TAB -->
        <div v-else class="w-full max-w-md px-0">
            <!-- Logo above card -->
            <div class="mb-6 text-center">
                <h1 class="font-display-product text-3xl font-bold text-primary tracking-tight mb-1">ADSIS</h1>
                <p class="font-mono text-xs uppercase text-slate tracking-widest">Nusantara Tech</p>
            </div>

            <div class="bg-canvas-white rounded-lg border border-hairline p-8">
                <div class="mb-6 text-center">
                    <h2 class="text-2xl font-semibold text-primary tracking-tight mb-1">Create Account</h2>
                    <p class="text-slate text-sm">Enter your details to register for the platform.</p>
                </div>

                <form @submit.prevent="register" class="space-y-4">
                    <div>
                        <label class="block font-mono text-xs uppercase text-primary tracking-widest mb-2"
                            for="reg-name">Full Name</label>
                        <input v-model="registerForm.name" id="reg-name" type="text" required placeholder="Jane Doe"
                            class="input-field" />
                    </div>
                    <div>
                        <label class="block font-mono text-xs uppercase text-primary tracking-widest mb-2"
                            for="reg-nim">NIM</label>
                        <input v-model="registerForm.nim" id="reg-nim" type="text" required placeholder="2451xxxxxx"
                            class="input-field" />
                    </div>
                    <div>
                        <label class="block font-mono text-xs uppercase text-primary tracking-widest mb-2"
                            for="reg-email">Email</label>
                        <input v-model="registerForm.email" id="reg-email" type="email"
                            placeholder="johndoe@example.com" class="input-field" />
                    </div>
                    <div>
                        <label class="block font-mono text-xs uppercase text-primary tracking-widest mb-2"
                            for="reg-password">Password</label>
                        <input v-model="registerForm.password" id="reg-password" type="password" required
                            placeholder="••••••••" class="input-field" />
                    </div>
                    <div class="pt-2">
                        <button type="submit" :disabled="loading" class="btn-primary w-full">
                            <span v-if="loading" class="material-symbols-outlined animate-spin"
                                style="font-size:16px;">progress_activity</span>
                            {{ loading ? "Registering..." : "Register" }}
                        </button>
                    </div>
                </form>

                <div class="mt-6 text-center text-sm text-slate">
                    Already have an account?
                    <button @click="authTab = 'login'"
                        class="text-ink underline hover:text-action-blue ml-1 transition-colors">Log in here</button>
                </div>
            </div>
        </div>
    </div>

    <!-- ===================== DASHBOARD VIEW ===================== -->
    <div v-if="view === 'dashboard'" class="min-h-screen bg-background font-body-md text-on-background flex">

        <!-- Sidebar (Desktop) -->
        <aside
            class="hidden md:flex flex-col bg-surface-container text-on-surface h-full w-64 border-r border-hairline fixed left-0 top-0 pt-20 pb-8 px-4 z-40">
            <div class="mb-6 px-4">
                <h2 class="font-display-product text-lg font-bold text-primary">ADSIS</h2>
                <p class="font-mono text-xs text-slate uppercase tracking-widest mt-1">Nusantara Tech</p>
            </div>

            <nav class="flex-1 flex flex-col gap-1">
                <button @click="uploadView = false" :class="!uploadView ? 'nav-item-active' : 'nav-item'"
                    class="text-left w-full">
                    <span class="material-symbols-outlined">image</span>
                    Library
                </button>
                <button @click="uploadView = true" :class="uploadView ? 'nav-item-active' : 'nav-item'"
                    class="text-left w-full">
                    <span class="material-symbols-outlined">upload</span>
                    Upload
                </button>
            </nav>

            <div class="mt-auto flex flex-col gap-1 pt-4 border-t border-hairline">
                <!-- User info -->
                <div class="px-4 py-2 mb-2">
                    <p class="text-sm font-semibold text-primary truncate">{{ user?.name }}</p>
                    <p class="text-xs text-slate truncate">{{ user?.nim }}</p>
                </div>
                <button @click="logout" class="nav-item text-left w-full text-error-red hover:bg-red-50">
                    <span class="material-symbols-outlined" style="color:inherit;">logout</span>
                    Logout
                </button>
            </div>
        </aside>

        <!-- Mobile Top Bar -->
        <div
            class="md:hidden fixed top-0 left-0 right-0 z-40 bg-canvas-white border-b border-hairline px-4 py-3 flex items-center justify-between">
            <div>
                <span class="font-display-product font-bold text-primary text-base">ADSIS</span>
                <span class="font-mono text-xs text-slate uppercase tracking-widest ml-2">Nusantara Tech</span>
            </div>
            <button @click="logout"
                class="text-xs text-slate hover:text-error-red transition-colors flex items-center gap-1">
                <span class="material-symbols-outlined" style="font-size:16px;">logout</span>
                Logout
            </button>
        </div>

        <!-- Main Content -->
        <div class="flex-1 md:ml-64 flex flex-col min-h-screen w-full">

            <!-- ===== LIBRARY VIEW ===== -->
            <main v-if="!uploadView"
                class="flex-1 bg-canvas-white pt-20 md:pt-24 pb-16 px-4 md:px-10 max-w-[1200px] mx-auto w-full">
                <!-- Page Header -->
                <div
                    class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 border-b border-hairline pb-6 gap-4">
                    <div>
                        <h2 class="text-2xl md:text-4xl font-semibold text-primary tracking-tight">Library Overview</h2>
                        <p class="text-slate text-sm mt-1">Manage and curate your dataset assets.</p>
                    </div>
                    <button @click="uploadView = true" class="btn-primary shrink-0">
                        <span class="material-symbols-outlined" style="font-size:18px;">add_photo_alternate</span>
                        Add New Image
                    </button>
                </div>

                <!-- Empty state -->
                <div v-if="files.length === 0" class="flex flex-col items-center justify-center py-24 text-center">
                    <span class="material-symbols-outlined text-muted-slate mb-4"
                        style="font-size:48px;">photo_library</span>
                    <p class="text-slate text-base">No files uploaded yet.</p>
                    <button @click="uploadView = true" class="btn-primary mt-6">
                        <span class="material-symbols-outlined" style="font-size:16px;">upload</span>
                        Upload Your First File
                    </button>
                </div>

                <!-- Image Grid -->
                <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <article v-for="file in files" :key="file.id" class="image-card group">
                        <!-- Thumbnail -->
                        <div class="h-48 w-full bg-surface-container-low relative overflow-hidden">
                            <img v-if="isImage(file.original_name)" :src="`/api/files/${file.original_name}`"
                                :alt="file.original_name"
                                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
                            <div v-else
                                class="w-full h-full flex flex-col items-center justify-center text-muted-slate">
                                <span class="material-symbols-outlined" style="font-size:40px;">description</span>
                                <span class="text-xs mt-2 font-mono uppercase">{{ getFileExt(file.original_name)
                                    }}</span>
                            </div>
                        </div>

                        <!-- Card Info -->
                        <div class="p-4 flex flex-col gap-2 border-t border-hairline bg-surface-container-low">
                            <div class="flex justify-between items-start">
                                <h3 class="text-sm font-semibold text-primary truncate pr-2">{{ file.original_name }}
                                </h3>
                                <span
                                    class="font-mono text-xs uppercase text-slate shrink-0 bg-surface-container px-2 py-0.5 rounded">{{
                                    getFileExt(file.original_name) }}</span>
                            </div>
                            <p class="text-xs text-slate">{{ formatDate(file.uploaded_at) }}</p>
                            <div class="flex items-center gap-4 mt-1 pt-2 border-t border-hairline">
                                <button @click="downloadFile(file.original_name)"
                                    class="text-sm text-action-blue hover:underline underline-offset-4 font-medium transition-colors flex items-center gap-1">
                                    <span class="material-symbols-outlined" style="font-size:14px;">download</span>
                                    Download
                                </button>
                                <button @click="deleteFile(file.original_name)"
                                    class="text-sm text-error-red hover:underline underline-offset-4 font-medium transition-colors flex items-center gap-1">
                                    <span class="material-symbols-outlined" style="font-size:14px;">delete</span>
                                    Delete
                                </button>
                            </div>
                        </div>
                    </article>
                </div>
            </main>

            <!-- ===== UPLOAD VIEW ===== -->
            <main v-if="uploadView" class="flex-1 flex flex-col min-h-screen">
                <!-- Context Header Band -->
                <div class="bg-secondary text-on-secondary pt-20 md:pt-24 pb-6 px-4 md:px-10 border-b border-hairline">
                    <div
                        class="max-w-[1200px] mx-auto w-full flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div>
                            <h1 class="text-2xl md:text-3xl font-semibold text-on-secondary tracking-tight">Media Upload
                            </h1>
                            <p class="text-secondary-fixed-dim text-sm mt-1">Add new assets to your operational library.
                            </p>
                        </div>
                        <button @click="uploadView = false"
                            class="flex items-center gap-2 text-secondary-fixed-dim hover:text-on-secondary text-sm transition-colors">
                            <span class="material-symbols-outlined" style="font-size:16px;">arrow_back</span>
                            Back to Library
                        </button>
                    </div>
                </div>

                <!-- Canvas -->
                <div class="flex-1 w-full max-w-[1200px] mx-auto p-4 md:p-10 bg-surface">
                    <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">

                        <!-- Left: Form -->
                        <div class="lg:col-span-5 flex flex-col gap-6">
                            <div class="bg-canvas-white p-6 rounded-lg border border-hairline flex flex-col gap-5">
                                <h3 class="font-semibold text-base border-b border-hairline pb-3">Upload File</h3>

                                <form @submit.prevent="uploadFile" class="flex flex-col gap-5">
                                    <!-- File Picker -->
                                    <div class="flex flex-col gap-2">
                                        <label class="font-mono text-xs uppercase text-slate tracking-widest">Select
                                            File</label>
                                        <div class="border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center gap-3 transition-colors cursor-pointer"
                                            :class="isDragging ? 'border-form-focus-violet bg-surface-container' : 'border-hairline bg-surface hover:border-form-focus-violet'"
                                            @click="$refs.fileInput.click()" @dragover.prevent="onDragOver"
                                            @dragleave.prevent="onDragLeave" @drop.prevent="onDrop">
                                            <span class="material-symbols-outlined text-muted-slate"
                                                style="font-size:36px;">upload_file</span>
                                            <p class="text-sm text-slate text-center">
                                                <span v-if="selectedFile" class="text-primary font-medium">{{
                                                    selectedFile.name }}</span>
                                                <span v-else>Click to choose a file or drag & drop</span>
                                            </p>
                                            <p v-if="selectedFile" class="text-xs text-muted-slate">{{
                                                (selectedFile.size / 1024 / 1024).toFixed(2) }} MB</p>
                                        </div>
                                        <input ref="fileInput" type="file" @change="onFileChange" class="hidden" />
                                    </div>

                                    <!-- Submit Button -->
                                    <button type="submit" :disabled="loading || !selectedFile"
                                        class="btn-primary w-full">
                                        <span v-if="loading" class="material-symbols-outlined animate-spin"
                                            style="font-size:16px;">progress_activity</span>
                                        <span v-else class="material-symbols-outlined"
                                            style="font-size:16px;">cloud_upload</span>
                                        {{ loading ? "Uploading..." : "Upload to Library" }}
                                    </button>
                                </form>
                            </div>
                        </div>

                        <!-- Right: Preview -->
                        <div class="lg:col-span-7 flex flex-col">
                            <div
                                class="bg-canvas-white rounded-media border border-hairline overflow-hidden flex flex-col h-full sticky top-24">
                                <!-- Preview header -->
                                <div
                                    class="bg-surface-container-low flex items-center gap-2 p-4 border-b border-hairline">
                                    <span class="material-symbols-outlined text-slate"
                                        style="font-size:18px;">visibility</span>
                                    <span class="font-mono text-xs text-slate uppercase tracking-widest">Preview
                                        Source</span>
                                </div>

                                <!-- Preview area -->
                                <div
                                    class="flex-1 bg-surface-container-lowest p-4 relative flex items-center justify-center min-h-[300px] md:min-h-[400px]">
                                    <!-- Checkered bg -->
                                    <div class="absolute inset-0 z-0 opacity-20"
                                        style="background-image: linear-gradient(45deg, #e5e7eb 25%, transparent 25%), linear-gradient(-45deg, #e5e7eb 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #e5e7eb 75%), linear-gradient(-45deg, transparent 75%, #e5e7eb 75%); background-size: 20px 20px; background-position: 0 0, 0 10px, 10px -10px, -10px 0px;">
                                    </div>

                                    <template v-if="selectedFile && isImage(selectedFile.name)">
                                        <img :src="getObjectUrl(selectedFile)" :alt="selectedFile.name"
                                            class="relative z-10 max-w-full max-h-[500px] object-contain rounded shadow-sm border border-hairline" />
                                    </template>
                                    <template v-else-if="selectedFile">
                                        <div class="relative z-10 flex flex-col items-center gap-3 text-slate">
                                            <span class="material-symbols-outlined"
                                                style="font-size:56px;">description</span>
                                            <p class="text-sm font-medium text-primary">{{ selectedFile.name }}</p>
                                            <p class="font-mono text-xs uppercase text-slate">{{
                                                getFileExt(selectedFile.name) }} · {{ (selectedFile.size / 1024 /
                                                1024).toFixed(2) }} MB</p>
                                        </div>
                                    </template>
                                    <template v-else>
                                        <div class="relative z-10 flex flex-col items-center gap-3 text-muted-slate">
                                            <span class="material-symbols-outlined"
                                                style="font-size:56px;">image_search</span>
                                            <p class="text-sm">Select a file to preview it here</p>
                                        </div>
                                    </template>
                                </div>

                                <!-- Preview footer -->
                                <div class="bg-surface p-4 border-t border-hairline flex justify-between items-center">
                                    <span class="text-xs text-slate font-mono">
                                        {{ selectedFile ? selectedFile.name : 'No file selected' }}
                                    </span>
                                    <button v-if="selectedFile" @click="selectedFile = null"
                                        class="text-sm text-error-red hover:underline transition-colors">
                                        Clear
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </main>

            <!-- Mobile Bottom Nav -->
            <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-canvas-white border-t border-hairline flex z-40">
                <button @click="uploadView = false"
                    class="flex-1 flex flex-col items-center py-3 gap-1 text-xs font-mono uppercase tracking-widest transition-colors"
                    :class="!uploadView ? 'text-primary' : 'text-slate'">
                    <span class="material-symbols-outlined" style="font-size:20px;">image</span>
                    Library
                </button>
                <button @click="uploadView = true"
                    class="flex-1 flex flex-col items-center py-3 gap-1 text-xs font-mono uppercase tracking-widest transition-colors"
                    :class="uploadView ? 'text-primary' : 'text-slate'">
                    <span class="material-symbols-outlined" style="font-size:20px;">upload</span>
                    Upload
                </button>
            </nav>
        </div>
    </div>
</template>
