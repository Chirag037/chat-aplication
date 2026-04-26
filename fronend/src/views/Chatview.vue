<template>
  <div class="flex h-screen bg-white overflow-hidden font-sans text-slate-900 selection:bg-slate-200">
    <!-- Sidebar -->
    <Sidebar 
      :activeRoomId="roomId" 
      :isOpen="isSidebarOpen" 
      @select-room="handleRoomSelect" 
      @close="isSidebarOpen = false"
    />
    
    <!-- Main Chat Area -->
    <div class="flex-1 flex flex-col min-w-0 bg-white overflow-hidden">
      
      <!-- Minimalist Header -->
      <header class="h-14 flex items-center justify-between px-6 bg-white border-b border-slate-100 z-10 shrink-0">
        <div class="flex items-center gap-3">
          <button @click="isSidebarOpen = true" class="md:hidden p-2 -ml-2 text-slate-400 hover:bg-slate-50 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
          </button>
          <div>
            <h2 class="text-sm font-bold text-slate-900 tracking-tight">{{ currentRoomName }}</h2>
            <div v-if="roomId" class="flex items-center gap-1.5 py-0.5">
              <span class="w-1 h-1 bg-slate-200 rounded-full"></span>
              <span class="text-[9px] font-bold text-slate-400 uppercase tracking-[0.15em]">Direct Message</span>
            </div>
          </div>
        </div>
        
        <div class="flex items-center gap-6">
          <div class="hidden sm:flex items-center gap-3">
            <span class="text-[10px] font-bold text-slate-300 uppercase tracking-widest">{{ currentUser }}</span>
            <div class="w-7 h-7 bg-slate-50 border border-slate-100 rounded-lg flex items-center justify-center text-[10px] font-bold text-slate-400">
              {{ getInitial(currentUser) }}
            </div>
          </div>
          <button @click="logout" class="text-[10px] font-bold text-slate-400 hover:text-slate-900 uppercase tracking-widest transition-colors duration-200">
            Sign Out
          </button>
        </div>
      </header>

      <!-- Message Display -->
      <main class="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 bg-slate-50 transition-colors duration-300" ref="messageWindow">
        <div 
          v-for="(msg, index) in messages" 
          :key="msg.id || index" 
          :class="['flex flex-col w-full', msg.username === currentUser ? 'items-end' : 'items-start']"
        >
          <!-- Metadata -->
          <div class="flex items-center gap-2 mb-1 px-1 opacity-60">
             <span v-if="msg.username !== currentUser" class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
              {{ msg.username }}
            </span>
            <span class="text-[9px] font-medium text-slate-300 uppercase letter-spacing-wide">
              {{ formatTime(msg.created_at) }}
            </span>
          </div>

          <!-- Bubble Container -->
          <div class="group relative flex items-center">
            <!-- Edit/Delete Actions (Left side for sent messages) -->
            <div v-if="msg.username === currentUser && editingMessageId !== msg.id" class="hidden group-hover:flex items-center gap-1 mr-2 bg-white/10 backdrop-blur-md border border-white/10 rounded-lg p-1 transition-all duration-200">
              <button @click="startEdit(msg)" class="p-1 hover:bg-white/20 rounded transition-colors" title="Edit message">
                <svg class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"/></svg>
              </button>
              <button @click="deleteMessage(msg.id)" class="p-1 hover:bg-red-500/20 rounded transition-colors" title="Delete message">
                <svg class="w-3 h-3 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
              </button>
            </div>

            <!-- Bubble Content -->
            <div 
              :class="[
                'px-5 py-3 shadow-sm transition-all duration-300 text-sm leading-relaxed min-w-[60px]',
                msg.username === currentUser 
                  ? 'bg-green-100 text-green-900 rounded-xl rounded-tr-none border border-green-200' 
                  : 'bg-blue-100 text-blue-900 rounded-xl rounded-tl-none border border-blue-200'
              ]"
            >
              <!-- Normal View -->
              <div v-if="editingMessageId !== msg.id">
                <!-- Text Content (if any) -->
                <p v-if="msg.content" class="whitespace-pre-wrap">{{ msg.content }}</p>

                <!-- Media Content -->
                <div v-if="msg.attachment" class="mt-2 rounded-xl overflow-hidden shadow-sm bg-black/5 border border-black/5 group/media relative">
                  
                  <!-- Image Display -->
                  <div v-if="msg.message_type === 'image'" class="relative max-h-[320px] max-w-[320px] flex items-center justify-center bg-black/5 overflow-hidden">
                    <img :src="processMediaUrl(msg.attachment)" class="w-full h-full object-cover hover:brightness-105 transition-all cursor-zoom-in" @click="openMedia(processMediaUrl(msg.attachment))" />
                    <!-- Hover Download Overlay -->
                    <div class="absolute inset-0 bg-black/20 opacity-0 group-hover/media:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                      <button @click.stop="downloadFile(processMediaUrl(msg.attachment))" class="pointer-events-auto p-2 bg-white/90 rounded-full shadow-lg hover:bg-white transition-colors" title="Download Image">
                        <svg class="w-5 h-5 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                      </button>
                    </div>
                  </div>

                  <!-- Video Display -->
                  <div v-else-if="msg.message_type === 'video'" class="relative group/vid">
                    <video 
                      :src="processMediaUrl(msg.attachment) + '#t=0.5'" 
                      preload="metadata" 
                      controls 
                      playsinline 
                      webkit-playsinline 
                      crossorigin="anonymous"
                      class="max-w-full block rounded-lg bg-black min-h-[150px]"
                    >
                      Your browser does not support the video tag.
                    </video>
                    <!-- Hover Actions -->
                    <div class="absolute top-2 right-2 flex gap-2 opacity-0 group-hover/vid:opacity-100 transition-opacity">
                      <button @click.stop="openMedia(processMediaUrl(msg.attachment))" class="p-1.5 bg-white/80 rounded-lg shadow-sm hover:bg-white" title="Open in New Tab">
                        <svg class="w-4 h-4 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                      </button>
                      <button @click.stop="downloadFile(processMediaUrl(msg.attachment))" class="p-1.5 bg-white/80 rounded-lg shadow-sm hover:bg-white" title="Download Video">
                        <svg class="w-4 h-4 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                      </button>
                    </div>
                  </div>
                  
                  <!-- Voice Message Display -->
                  <div v-else-if="msg.message_type === 'voice'" class="flex items-center gap-3 p-3 bg-white/40 hover:bg-white/60 transition-colors rounded-lg">
                    <!-- Play/Pause Button -->
                    <button 
                      @click="toggleVoicePlayback(msg.id, msg.attachment)" 
                      class="shrink-0 p-2.5 bg-white/80 rounded-full shadow-sm hover:bg-white transition-colors group/play"
                      :title="isPlaying[msg.id] ? 'Pause' : 'Play'"
                    >
                      <svg v-if="!isPlaying[msg.id]" class="w-4 h-4 text-slate-700 group-hover/play:text-slate-900" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
                      <svg v-else class="w-4 h-4 text-slate-700 group-hover/play:text-slate-900" fill="currentColor" viewBox="0 0 24 24"><path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/></svg>
                    </button>
                    
                    <!-- Progress Bar & Time Display -->
                    <div class="flex-1 min-w-0">
                      <!-- Progress Bar -->
                      <div 
                        @click="seekVoicePlayback(msg.id, $event)"
                        class="h-1.5 bg-white/50 rounded-full cursor-pointer group/progress overflow-hidden hover:h-2 transition-all"
                        :title="`${formatPlaybackTime(playbackTime[msg.id] || 0)} / ${formatPlaybackTime(msg.duration || 0)}`"
                      >
                        <div 
                          class="h-full bg-gradient-to-r from-blue-400 to-blue-500 rounded-full transition-all"
                          :style="{ width: getPlaybackProgress(msg.id) + '%' }"
                        ></div>
                      </div>
                      <!-- Time Display -->
                      <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-1">
                        {{ formatPlaybackTime(playbackTime[msg.id] || 0) }} / {{ formatPlaybackTime(msg.duration || 0) }}s
                      </p>
                    </div>
                    
                    <!-- Download Button -->
                    <button 
                      @click="downloadFile(processMediaUrl(msg.attachment))" 
                      class="shrink-0 p-2 text-slate-400 hover:text-slate-900 transition-colors" 
                      title="Download"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                    </button>

                    <!-- Transcribe Button -->
                    <button 
                      @click="openTranscribeModal(msg.id, processMediaUrl(msg.attachment))" 
                      class="shrink-0 p-2 text-indigo-400 hover:text-indigo-600 transition-colors relative group/transcribe" 
                      title="Transcribe to text"
                      :disabled="isTranscribing[msg.id]"
                    >
                      <svg v-if="!isTranscribing[msg.id]" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4"/></svg>
                      <svg v-else class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                      <span class="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-900 text-white text-[9px] px-2 py-1 rounded opacity-0 group-hover/transcribe:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">Transcribe</span>
                    </button>
                  </div>
                  
                  <!-- Transcribed Text Area -->
                  <div v-if="transcriptions[msg.id]" class="px-3 pb-3 -mt-1">
                    <div class="p-2 bg-white/40 rounded border border-black/5 text-[11px] text-slate-800 italic leading-snug relative group/text space-y-2">
                       <div :class="{'opacity-50': isProcessingAI[msg.id]}">"{{ transcriptions[msg.id] }}"</div>
                       
                       <!-- AI Tools -->
                       <div class="flex items-center gap-3 pt-1.5 border-t border-black/5">
                         <button @click="processAI('summarize', msg.id, transcriptions[msg.id])" 
                                 class="text-[9px] font-bold text-indigo-500 hover:text-indigo-700 uppercase tracking-tight flex items-center gap-1 disabled:opacity-50"
                                 :disabled="isProcessingAI[msg.id]">
                           <svg v-if="!isProcessingAI[msg.id]" class="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/></svg>
                           <svg v-else class="w-2.5 h-2.5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                           Summarize
                         </button>
                         <button @click="processAI('rephrase', msg.id, transcriptions[msg.id])" 
                                 class="text-[9px] font-bold text-indigo-500 hover:text-indigo-700 uppercase tracking-tight flex items-center gap-1 disabled:opacity-50"
                                 :disabled="isProcessingAI[msg.id]">
                           <svg v-if="!isProcessingAI[msg.id]" class="w-2.5 h-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5L6 9H2v6h4l5 4V5z"/></svg>
                           <svg v-else class="w-2.5 h-2.5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                           Fix & Rephrase
                         </button>

                         <button @click="copyToClipboard(transcriptions[msg.id])" class="ml-auto p-1 text-slate-400 hover:text-indigo-600 transition-opacity" title="Copy text">
                           <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
                         </button>
                       </div>

                       <!-- AI Result: Summary -->
                       <div v-if="aiSummaries[msg.id]" class="p-2 bg-indigo-50/50 rounded text-[10px] text-indigo-700 border border-indigo-100/50 animate-in fade-in slide-in-from-top-1">
                         <span class="font-bold uppercase text-[8px] block mb-0.5 opacity-60">AI Summary</span>
                         {{ aiSummaries[msg.id] }}
                       </div>
                    </div>
                  </div>

                  <!-- File / Document Card -->
                  <div v-else class="flex items-center gap-4 p-4 bg-white/40 hover:bg-white/60 transition-colors cursor-pointer" @click="downloadFile(msg.attachment)">
                    <div class="shrink-0 w-10 h-10 flex items-center justify-center bg-white/80 rounded-xl shadow-sm border border-black/5">
                      <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                    </div>
                    <div class="flex-1 min-w-0 pr-2">
                      <p class="text-[11px] font-bold text-slate-700 truncate mb-0.5">{{ getFileName(msg.attachment) }}</p>
                      <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">{{ getFileExt(msg.attachment) }} File</p>
                    </div>
                    <div class="shrink-0">
                       <button class="p-2 text-slate-400 hover:text-indigo-600 transition-colors">
                          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                       </button>
                    </div>
                  </div>
                </div>

                <div class="mt-1.5 flex items-center justify-end gap-1.5 px-0.5">
                  <span class="text-[9px] font-medium opacity-60 uppercase tracking-tighter">
                    {{ formatTime(msg.created_at) }}
                  </span>
                  <span v-if="msg.is_edited" class="text-[8px] italic opacity-40">Edited</span>
                </div>
              </div>

              <!-- Inline Edit View -->
              <div v-else class="flex flex-col gap-2 min-w-[200px]">
                <textarea 
                  v-model="editingContent" 
                  class="w-full bg-white/50 border border-green-300 rounded-lg p-2 text-sm text-green-900 outline-none focus:ring-2 focus:ring-green-400 resize-none"
                  rows="2"
                  @keyup.esc="cancelEdit"
                  @keyup.enter.exact.prevent="saveEdit"
                ></textarea>
                <div class="flex justify-end gap-2">
                  <button @click="cancelEdit" class="text-[10px] font-bold text-slate-500 uppercase tracking-widest hover:text-slate-700">Cancel</button>
                  <button @click="saveEdit" class="text-[10px] font-bold text-green-600 uppercase tracking-widest hover:text-green-800">Save</button>
                </div>
              </div>
            </div>

            <!-- Status Icons & Seen By -->
            <div v-if="msg.username === currentUser" class="absolute -bottom-5 right-1 flex items-center gap-2 h-4">
              <!-- Seen By (Group rooms only) - Shown to the left of the icon -->
              <span v-if="msg.seen_by && msg.seen_by.length > 0" class="text-[8px] text-blue-500 font-bold whitespace-nowrap">
                Seen by {{ msg.seen_by.join(', ') }}
              </span>

              <!-- Viewed (Blue Circle) -->
              <div v-if="msg.status === 'viewed' || (msg.seen_by && msg.seen_by.length > 0)" class="w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_6px_rgba(59,130,246,0.6)] border border-blue-400"></div>
              
              <!-- Delivered (Double Tick) -->
              <div v-else-if="msg.status === 'delivered'" class="flex -space-x-1.5 opacity-60">
                <svg class="w-3 h-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
                <svg class="w-3 h-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
              </div>
              
              <!-- Sent (Single Tick) -->
              <div v-else class="opacity-30">
                <svg class="w-3 h-3 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/></svg>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty States -->
        <div v-if="!roomId" class="h-full flex flex-col items-center justify-center text-center px-4 max-w-sm mx-auto">
          <div class="w-12 h-12 bg-slate-50 border border-slate-100 rounded-2xl flex items-center justify-center mb-6">
            <svg class="w-6 h-6 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
          </div>
          <h3 class="text-sm font-bold text-slate-900 uppercase tracking-wider">No Active Session</h3>
          <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">Select a destination from the sidebar to begin your communication session.</p>
        </div>
        
        <div v-else-if="messages.length === 0" class="h-full flex items-center justify-center">
          <p class="text-[10px] font-bold text-slate-300 uppercase tracking-[0.3em] italic">Session Initialized</p>
        </div>
      </main>

      <!-- Minimalist Input Bar -->
      <footer class="p-6 md:p-8 bg-white shrink-0 shadow-[0_-1px_0_0_rgba(241,245,249,1)]">
        <!-- Recording Indicator -->
        <div v-if="isRecording" class="flex items-center justify-center gap-2 mb-4 p-3 bg-red-50 border border-red-100 rounded-lg">
          <div class="flex gap-1">
            <div class="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse"></div>
            <div class="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" style="animation-delay: 0.1s;"></div>
            <div class="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" style="animation-delay: 0.2s;"></div>
          </div>
          <span class="text-sm font-bold text-red-600">Recording... {{ recordingTime }}s</span>
        </div>

        <!-- File/Image Preview before sending -->
        <div v-if="selectedFile && isImage(selectedFile)" class="mb-4 relative inline-block">
          <img :src="filePreview" class="w-20 h-20 object-cover rounded-xl border-2 border-slate-100 shadow-sm" />
          <button @click="clearFile" class="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full shadow-md hover:bg-red-600 transition-colors">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>
        <div v-else-if="selectedFile" class="mb-4 flex items-center gap-3 p-3 bg-slate-50 border border-slate-100 rounded-xl max-w-xs">
          <div class="w-10 h-10 flex items-center justify-center bg-white rounded-lg shadow-sm border border-slate-200">
            <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-bold text-slate-700 truncate">{{ selectedFile.name }}</p>
            <p class="text-[10px] text-slate-400 uppercase tracking-widest">{{ (selectedFile.size / 1024).toFixed(1) }} KB</p>
          </div>
          <button @click="clearFile" class="text-slate-400 hover:text-red-500 transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          </button>
        </div>

        <div v-if="selectedVoiceMessage && !isRecording" class="flex items-center justify-between mb-4 p-3 bg-green-50 border border-green-100 rounded-lg">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            <span class="text-sm font-bold text-green-600">Voice Message Ready ({{ selectedVoiceMessage.duration }}s)</span>
          </div>
          <div class="flex items-center gap-3">
            <!-- AI Refine for Input -->
            <button 
              v-if="newMessage.trim() && !isRecording"
              @click="processAI('rephrase', 'input', newMessage)" 
              class="text-xs font-bold text-indigo-400 hover:text-indigo-600 uppercase tracking-widest flex items-center gap-1"
              :disabled="isProcessingAI['input']"
              title="Fix grammar and rephrase"
            >
              <svg v-if="!isProcessingAI['input']" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
              <svg v-else class="w-3 h-3 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              {{ isProcessingAI['input'] ? 'Refining...' : 'AI Fix' }}
            </button>

            <button 
              @click="openTranscribeModal(null, null, true)" 
              class="text-xs font-bold text-indigo-600 hover:text-indigo-700 uppercase tracking-widest flex items-center gap-1"
              :disabled="isTranscribing['input']"
            >
              <svg v-if="!isTranscribing['input']" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4"/></svg>
              <svg v-else class="w-3 h-3 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
              {{ isTranscribing['input'] ? 'Transcribing...' : 'Transcribe to Text' }}
            </button>
            <button @click="cancelVoiceRecording" class="text-xs font-bold text-green-600 hover:text-green-700 uppercase tracking-widest">Cancel</button>
          </div>
        </div>

        <div class="w-full flex items-center gap-4">
          <div class="flex-1 flex items-center bg-slate-50 border border-slate-100 rounded-xl focus-within:bg-white focus-within:border-slate-900 focus-within:shadow-lg focus-within:shadow-slate-200/20 transition-all duration-200 overflow-hidden">
            <!-- Hidden File Input -->
            <input type="file" ref="fileInput" class="hidden" @change="handleFileChange" />
            
            <!-- File Upload Button -->
            <button 
              @click="triggerFileInput" 
              class="pl-5 pr-2 text-slate-400 hover:text-slate-900 transition-colors"
              title="Attach media"
              :disabled="sending || isRecording"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
            </button>
            
            <!-- Microphone Button -->
            <button 
              @click="toggleVoiceRecording" 
              :class="[
                'px-2 transition-colors',
                isRecording ? 'text-red-500 hover:text-red-600' : 'text-slate-400 hover:text-slate-900'
              ]"
              title="Record voice message"
              :disabled="sending"
            >
              <svg v-if="!isRecording" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4"/></svg>
              <svg v-else class="w-5 h-5 animate-pulse" fill="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="8"/></svg>
            </button>

            <!-- Dictation (Speech to Text) Button -->
            <button 
              @click="toggleDictation" 
              :class="[
                'px-2 transition-all duration-200',
                isDictating ? 'text-indigo-500 scale-110' : 'text-slate-400 hover:text-indigo-500'
              ]"
              :disabled="sending || isRecording"
              title="Speak to type (Dictation)"
            >
              <svg v-if="!isDictating" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5L6 9H2v6h4l5 4V5zM15.54 8.46a5 5 0 010 7.07M19.07 4.93a10 10 0 010 14.14"/></svg>
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
            </button>

            <input 
              v-model="newMessage" 
              @keyup.enter="sendMessage" 
              ref="textInput"
              :placeholder="isRecording ? 'Recording...' : (selectedFile ? 'Add a caption...' : (selectedVoiceMessage ? 'Voice ready to send' : 'Start typing...'))"
              type="text"
              :disabled="sending || isRecording"
              class="flex-1 bg-transparent px-3 py-3.5 text-sm placeholder-slate-300 outline-none disabled:opacity-50"
            />
            
            <button 
              v-if="selectedFile"
              @click="clearFile"
              class="px-2 text-red-400 hover:text-red-600 transition-colors"
              title="Clear file"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
            
            <button 
              v-if="selectedVoiceMessage"
              @click="cancelVoiceRecording"
              class="px-2 text-red-400 hover:text-red-600 transition-colors"
              title="Cancel voice message"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>

            <button 
              @click="sendMessage" 
              :disabled="(!newMessage.trim() && !selectedFile && !selectedVoiceMessage) || sending"
              class="px-5 group disabled:opacity-30"
            >
              <svg v-if="!sending" class="w-5 h-5 text-slate-400 group-hover:text-slate-900 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"/></svg>
              <svg v-else class="animate-spin h-4 w-4 text-slate-400" viewBox="0 0 24 24">
                <circle class="opacity-10" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-40" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </button>
          </div>
        </div>
      </footer>
    </div>

    <!-- Lightbox Overlay -->
    <Transition name="fade">
      <div v-if="lightboxImage" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 backdrop-blur-sm p-4 sm:p-10" @click="closeLightbox">
        <button @click="closeLightbox" class="absolute top-6 right-6 text-white/50 hover:text-white transition-colors p-2 rounded-full hover:bg-white/10 z-[110]">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
        
        <div class="relative max-w-full max-h-full flex items-center justify-center" @click.stop>
          <img :src="lightboxImage" class="max-w-full max-h-full object-contain rounded-lg shadow-2xl transition-all duration-300 transform scale-100" />
          
          <!-- Download Button in Lightbox -->
          <button @click="downloadFile(lightboxImage)" class="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-2 px-6 py-2.5 bg-white/10 hover:bg-white/20 text-white rounded-xl border border-white/20 backdrop-blur-md transition-all">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a2 2 0 002 2h12a2 2 0 002-2v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
            <span class="text-xs font-bold uppercase tracking-widest">Download Full Resolution</span>
          </button>
        </div>
      </div>
    </Transition>
    
    <!-- Transcription Choice Modal -->
    <Transition name="fade">
      <div v-if="showTranscribeModal" class="fixed inset-0 z-[110] flex items-center justify-center bg-black/60 backdrop-blur-sm p-4" @click="closeTranscribeModal">
        <div class="bg-white rounded-2xl shadow-2xl max-w-sm w-full overflow-hidden animate-in fade-in zoom-in duration-200" @click.stop>
          <div class="p-6">
            <h3 class="text-lg font-bold text-slate-900 mb-2">Transcribe Voice Message</h3>
            <p class="text-sm text-slate-500 mb-6 font-medium leading-relaxed">Choose your preferred transcription method. AI provides higher accuracy but requires an internet connection.</p>
            
            <div class="space-y-3">
              <button @click="handleTranscriptionChoice('normal')" class="w-full flex items-center gap-4 p-4 rounded-xl border border-slate-100 hover:border-indigo-100 hover:bg-slate-50 transition-all group text-left">
                <div class="w-10 h-10 flex items-center justify-center bg-slate-50 rounded-lg group-hover:bg-white transition-colors shrink-0">
                  <svg class="w-5 h-5 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4"/></svg>
                </div>
                <div>
                  <p class="text-sm font-bold text-slate-900">Normal Transcription</p>
                  <p class="text-[11px] text-slate-400 font-bold uppercase tracking-widest">Browser-based • Fast</p>
                </div>
              </button>
              
              <button @click="handleTranscriptionChoice('ai')" class="w-full flex items-center gap-4 p-4 rounded-xl border border-indigo-100 bg-indigo-50/30 hover:bg-indigo-50 transition-all group text-left">
                <div class="w-10 h-10 flex items-center justify-center bg-white rounded-lg shadow-sm shrink-0">
                  <svg class="w-5 h-5 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
                </div>
                <div>
                  <p class="text-sm font-bold text-indigo-900">AI Transcription</p>
                  <p class="text-[11px] text-indigo-400 font-bold uppercase tracking-widest">AssemblyAI • High Accuracy</p>
                </div>
              </button>
            </div>
          </div>
          
          <div class="p-4 bg-slate-50 flex justify-end">
            <button @click="closeTranscribeModal" class="px-4 py-2 text-xs font-bold text-slate-400 uppercase tracking-widest hover:text-slate-900 transition-colors">Cancel</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import axios from 'axios';
import api from '../api';
import Sidebar from '../components/Sidebar.vue';

export default {
  components: { Sidebar },
  data() {
    return {
      messages: [],
      newMessage: "",
      currentUser: localStorage.getItem('username') || "Guest",
      sending: false,
      roomId: localStorage.getItem('last_room_id') || null,
      currentRoomName: "Select Workspace",
      isSidebarOpen: false,
      socket: null,
      notifySocket: null,
      editingMessageId: null,
      editingContent: "",
      selectedFile: null,
      lightboxImage: null,
      mediaRecorder: null,
      audioChunks: [],
      isRecording: false,
      recordingTime: 0,
      recordingTimer: null,
      audioContext: null,
      selectedVoiceMessage: null,
      playingMessageId: null,
      currentAudio: null,
      playbackTime: {},
      isPlaying: {},
      playbackDuration: {},
      filePreview: null,
      isDictating: false,
      recognition: null,
      transcriptions: {},
      isTranscribing: {},
      showTranscribeModal: false,
      transcribeModalData: {
        messageId: null,
        audioUrl: null,
        audioBlob: null,
        isForInput: false
      },
      assemblyAIKey: "5734a76428f8474ab5ac0b7bc8dac395",
      isProcessingAI: {},
      aiSummaries: {},
      aiRephrased: {}
    };
  },
  methods: {
    getInitial(name) {
      return name ? name.charAt(0).toUpperCase() : '?';
    },
    async handleRoomSelect(payload) {
      const room = typeof payload === 'object' ? payload : null;
      const id = room ? room.id : payload;
      
      this.roomId = id;
      localStorage.setItem('last_room_id', id);
      this.isSidebarOpen = false;
      this.fetchMessages();
      this.initWebSocket();
      
      if (room) {
        if (room.type === 'direct') {
          const other = room.participants.find(p => p.username !== this.currentUser);
          this.currentRoomName = other ? other.username : 'Private Session';
        } else {
          this.currentRoomName = room.name || `Session ${room.id}`;
        }
      } else {
        // Fallback if just an ID is somehow passed
        try {
          const [groupRes, directRes] = await Promise.all([
            api.get('/api/rooms/group/'),
            api.get('/api/rooms/')
          ]);
          const allRooms = [...groupRes.data, ...directRes.data];
          const foundRoom = allRooms.find(r => r.id == id);
          if (foundRoom) {
            if (foundRoom.type === 'direct') {
              const other = foundRoom.participants.find(p => p.username !== this.currentUser);
              this.currentRoomName = other ? other.username : 'Private Session';
            } else {
              this.currentRoomName = foundRoom.name || `Session ${foundRoom.id}`;
            }
          }
        } catch (e) {
          console.error('Context error:', e);
        }
      }
    },
    initWebSocket() {
      if (this.socket) {
        this.socket.close();
      }

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const socketUrl = `${protocol}//${window.location.host}/ws/chat/${this.roomId}/`;
      
      this.socket = new WebSocket(socketUrl);

      this.socket.onopen = () => {
         this.socket.send(JSON.stringify({
            'action': 'join',
            'username': this.currentUser
         }));
         this.markRoomAsRead();
      };

      this.socket.onmessage = (e) => {
        const data = JSON.parse(e.data);
        if (data && data.room == this.roomId) {
          if (data.type === 'message' ) {
             this.messages.push({
               username: data.username,
               content: data.content,
               created_at: data.created_at,
               id: data.id || Date.now(),
               status: data.status || 'sent',
               room_type: data.room_type,
               message_type: data.message_type || 'text',
               attachment: data.attachment ? this.processMediaUrl(data.attachment) : null,
               duration: data.duration || null,
               seen_by: [],
             });
             this.$nextTick(this.scrollToBottom);
          } else if (data.type === 'delete') {
             this.messages = this.messages.filter(m => m.id !== data.message_id);
          } else if (data.type === 'edit') {
             const msg = this.messages.find(m => m.id === data.message_id);
             if (msg) {
               msg.content = data.content;
               msg.is_edited = true;
             }
          } else if (data.type === 'status_update') {
             // If the OTHER person updated their view/delivery status, update my sent messages
             if (data.username !== this.currentUser) {
               this.messages.forEach(m => {
                 if (m.username === this.currentUser) {
                    // Never downgrade: viewed > delivered > sent
                    if (data.status === 'viewed' && m.status !== 'viewed') {
                      m.status = 'viewed';
                    } 
                    else if (data.status === 'delivered' && m.status === 'sent') {
                      m.status = 'delivered';
                    }
                 }
               });
             }
           } else if (data.type === 'read_receipt') {
             // Group room: update the specific message's seen_by list
             const msg = this.messages.find(m => m.id === data.message_id);
             if (msg) {
               msg.seen_by = data.seen_by || [];
               // If this is the sender's own message and someone else saw it, mark as viewed
               if (msg.username === this.currentUser && msg.seen_by.length > 0) {
                 msg.status = 'viewed';
               }
             }
           }
        }
        
        // If we get a new message while in this room, mark it as read
        if (data.type === 'message' && data.username !== this.currentUser) {
          this.markRoomAsRead();
        }
      };

      this.socket.onclose = (e) => {
        console.log('Socket closed');
      };
    },

    initNotificationSocket() {
      if (this.notifySocket) return;

      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const socketUrl = `${protocol}//${window.location.host}/ws/notifications/`;
      
      this.notifySocket = new WebSocket(socketUrl);

      this.notifySocket.onopen = () => {
         this.notifySocket.send(JSON.stringify({
            'action': 'join',
            'username': this.currentUser
         }));
      };

      this.notifySocket.onclose = () => {
        this.notifySocket = null;
        setTimeout(this.initNotificationSocket, 3000);
      };
    },
    async fetchMessages() {
      if (!this.roomId) return;
      try {
        const response = await api.get(`/api/messages/?room_id=${this.roomId}`);
        this.messages = response.data.map(msg => {
          if (msg.attachment) {
            msg.attachment = this.processMediaUrl(msg.attachment);
          }
          return msg;
        });
        this.$nextTick(this.scrollToBottom);
      } catch (error) {
        console.error("Communication error:", error);
        if (error.response?.status === 401) {
          this.$router.push('/login');
        }
      }
    },

    async sendMessage() {
      if ((!this.newMessage.trim() && !this.selectedFile && !this.selectedVoiceMessage) || this.sending || !this.roomId) return;
      
      // Allow voice-only messages (no text required)
      if (!this.newMessage.trim() && !this.selectedFile && !this.selectedVoiceMessage) return;

      this.sending = true;
      try {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
          let payload = {
            'action': 'send',
            'message': this.newMessage,
            'username': this.currentUser
          };

          if (this.selectedFile) {
            const base64Data = await this.readFileAsBase64(this.selectedFile);
            let type = 'file';
            if (this.selectedFile.type.startsWith('image/')) type = 'image';
            else if (this.selectedFile.type.startsWith('video/')) type = 'video';

            payload.attachment = base64Data;
            payload.file_name = this.selectedFile.name;
            payload.message_type = type;
          } else if (this.selectedVoiceMessage) {
            const base64Data = await this.readFileAsBase64(this.selectedVoiceMessage.file);
            payload.attachment = base64Data;
            payload.file_name = this.selectedVoiceMessage.file.name;
            payload.message_type = 'voice';
            payload.duration = this.selectedVoiceMessage.duration;
            payload.message = ''; // No text content for voice-only messages
          }

          this.socket.send(JSON.stringify(payload));
          this.newMessage = "";
          this.clearFile();
          this.selectedVoiceMessage = null;
          this.recordingTime = 0;
        } else {
          alert("Connection lost. Please wait for reconnection or refresh the page.");
          this.initWebSocket(); // Try to reconnect
        }
        
        this.$nextTick(this.scrollToBottom);
      } catch (error) {
        console.error("Communication error:", error);
      } finally {
        this.sending = false;
      }
    },

    readFileAsBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = (error) => reject(error);
        reader.readAsDataURL(file);
      });
    },

    triggerFileInput() {
      this.$refs.fileInput.click();
    },

    handleFileChange(e) {
      const file = e.target.files[0];
      if (file) {
        this.selectedFile = file;
        if (this.isImage(file)) {
          this.filePreview = URL.createObjectURL(file);
        }
        // Focus the input so the user can just press Enter to send
        this.$nextTick(() => {
          if (this.$refs.textInput) this.$refs.textInput.focus();
        });
      }
    },

    isImage(file) {
      return file && file.type.startsWith('image/');
    },

    clearFile() {
      if (this.filePreview) {
        URL.revokeObjectURL(this.filePreview);
        this.filePreview = null;
      }
      this.selectedFile = null;
      if (this.$refs.fileInput) this.$refs.fileInput.value = '';
    },

    // Voice Recording Methods
    async toggleVoiceRecording() {
      if (this.isRecording) {
        this.stopRecording();
      } else {
        await this.startRecording();
      }
    },

    async startRecording() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.mediaRecorder = new MediaRecorder(stream);
        this.audioChunks = [];
        this.recordingTime = 0;
        this.isRecording = true;

        // Start recording timer
        this.recordingTimer = setInterval(() => {
          this.recordingTime++;
          // Stop recording at 60 seconds max
          if (this.recordingTime >= 60) {
            this.stopRecording();
          }
        }, 1000);

        this.mediaRecorder.ondataavailable = (event) => {
          this.audioChunks.push(event.data);
        };

        this.mediaRecorder.onstop = async () => {
          clearInterval(this.recordingTimer);
          await this.handleRecordingComplete();
        };

        this.mediaRecorder.start();
      } catch (error) {
        console.error("Microphone access denied:", error);
        alert("Microphone access required for voice messages. Please check your browser permissions.");
        this.isRecording = false;
      }
    },

    stopRecording() {
      if (this.mediaRecorder && this.isRecording) {
        this.mediaRecorder.stop();
        this.isRecording = false;
        if (this.mediaRecorder.stream) {
          this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }
      }
    },

    async handleRecordingComplete() {
      const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
      const file = new File([audioBlob], `voice_${Date.now()}.webm`, { type: 'audio/webm' });
      
      this.selectedVoiceMessage = {
        file: file,
        duration: this.recordingTime,
        blob: audioBlob
      };

      // Optional: autofocus/show that voice message is ready
      this.$nextTick(() => {
        if (this.$refs.textInput) this.$refs.textInput.focus();
      });
    },

    cancelVoiceRecording() {
      this.selectedVoiceMessage = null;
      this.recordingTime = 0;
    },

    openMedia(url) {
      this.lightboxImage = url;
      // Add escape listener for lightbox
      window.addEventListener('keydown', this.handleEsc);
    },

    closeLightbox() {
      this.lightboxImage = null;
      window.removeEventListener('keydown', this.handleEsc);
    },

    handleEsc(e) {
      if (e.key === 'Escape') this.closeLightbox();
    },

    downloadFile(url) {
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', '');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    },

    toggleVoicePlayback(messageId, url) {
      // If different audio is playing, stop it
      if (this.currentAudio && this.playingMessageId !== messageId) {
        this.currentAudio.pause();
        this.isPlaying[this.playingMessageId] = false;
      }

      // If this audio is already playing, pause it
      if (this.playingMessageId === messageId && this.isPlaying[messageId]) {
        this.currentAudio.pause();
        this.isPlaying[messageId] = false;
        return;
      }

      // If this audio was paused, resume it
      if (this.playingMessageId === messageId && !this.isPlaying[messageId]) {
        this.currentAudio.play();
        this.isPlaying[messageId] = true;
        return;
      }

      // Start new audio
      this.currentAudio = new Audio(this.processMediaUrl(url));
      this.playingMessageId = messageId;
      this.isPlaying[messageId] = true;

      // Update playback time during play
      this.currentAudio.ontimeupdate = () => {
        this.playbackTime[messageId] = this.currentAudio.currentTime;
      };

      // Store duration when metadata loads
      this.currentAudio.onloadedmetadata = () => {
        this.playbackDuration[messageId] = this.currentAudio.duration;
      };

      // Handle playback end
      this.currentAudio.onended = () => {
        this.isPlaying[messageId] = false;
        this.playingMessageId = null;
      };

      // Handle errors
      this.currentAudio.onerror = (error) => {
        console.error("Error playing voice message:", error);
        this.isPlaying[messageId] = false;
      };

      this.currentAudio.play().catch(error => {
        console.error("Error playing voice message:", error);
        this.isPlaying[messageId] = false;
      });
    },

    seekVoicePlayback(messageId, event) {
      if (!this.currentAudio || this.playingMessageId !== messageId) return;
      
      const progressBar = event.target;
      const rect = progressBar.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const percentage = x / rect.width;
      const seekTime = percentage * (this.playbackDuration[messageId] || this.currentAudio.duration);
      
      this.currentAudio.currentTime = Math.max(0, Math.min(seekTime, this.currentAudio.duration));
    },

    formatPlaybackTime(seconds) {
      if (!seconds || isNaN(seconds)) return '0:00';
      const mins = Math.floor(seconds / 60);
      const secs = Math.floor(seconds % 60);
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    getPlaybackProgress(messageId) {
      const current = this.playbackTime[messageId] || 0;
      const duration = this.playbackDuration[messageId] || 1;
      return (current / duration) * 100;
    },

    processMediaUrl(url) {
      if (!url) return null;
      if (typeof url !== 'string') return url;
      if (url.startsWith('/')) return url;
      try {
        const urlObj = new URL(url);
        return urlObj.pathname + urlObj.search;
      } catch (e) {
        return url.replace(/^https?:\/\/[^\/]+/, '');
      }
    },

    // Speech to Text (Dictation) Logic
    toggleDictation() {
      if (this.isDictating) {
        this.stopDictation();
      } else {
        this.startDictation();
      }
    },

    startDictation() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        alert("Your browser does not support Speech Recognition. Please try Chrome or Edge, and ensure you are on a secure (HTTPS) connection.");
        return;
      }

      this.recognition = new SpeechRecognition();
      this.recognition.continuous = true;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';

      // Keep track of the message before we started dictating to avoid double appending
      const originalMessage = this.newMessage;
      let lastFinalTranscript = '';

      this.recognition.onstart = () => {
        this.isDictating = true;
      };

      this.recognition.onresult = (event) => {
        let interimTranscript = '';
        let currentFinalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            currentFinalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        // We update the input field in real-time
        // We combine: original text + all final clips so far + current interim clip
        if (currentFinalTranscript) {
           lastFinalTranscript += (lastFinalTranscript ? ' ' : '') + currentFinalTranscript;
        }
        
        const combinedFinal = (originalMessage ? originalMessage + ' ' : '') + lastFinalTranscript;
        this.newMessage = combinedFinal + (interimTranscript ? ' ' + interimTranscript : '');
      };

      this.recognition.onerror = (event) => {
        console.error("Speech Recognition Error:", event.error);
        if (event.error === 'not-allowed') {
          alert("Microphone access denied. Please enable microphone permissions in your browser.");
        } else if (event.error === 'network') {
          alert("Network error during speech recognition. Please check your connection.");
        }
        this.stopDictation();
      };

      this.recognition.onend = () => {
        this.isDictating = false;
        // Strip any trailing spaces
        this.newMessage = this.newMessage.trim();
      };

      try {
        this.recognition.start();
      } catch (e) {
        console.error("Failed to start recognition:", e);
        this.isDictating = false;
      }
    },

    stopDictation() {
      if (this.recognition) {
        this.recognition.stop();
        this.isDictating = false;
      }
    },

    // Voice Message Transcription (Mock logic using Browser Speech Recognition)
    async transcribeVoiceMessage(messageId, audioUrl, audioBlob, isForInput) {
      if (this.isTranscribing[messageId]) return;
      
      this.isTranscribing[messageId] = true;
      
      // If we have a blob and it's for input, we can try to use SpeechRecognition
      // But for URLs (existing messages), we'd need to play them.
      
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        alert("Transcription requires a compatible browser (Chrome/Edge).");
        this.isTranscribing[messageId] = false;
        return;
      }

      // Note: Browser SpeechRecognition is designed for LIVE microphone input.
      // Doing "Normal" transcription on a file usually involves playing it.
      // Here we will use the existing mock-ish behavior or prompt the user.

      if (isForInput) {
          // If it's for input, we might as well use the AI option or tell them it's limited
          setTimeout(() => {
              this.isTranscribing[messageId] = false;
              alert("Normal transcription is limited for recorded files. AI Transcription is recommended for better results.");
          }, 1000);
          return;
      }

      const recognition = new SpeechRecognition();
      recognition.lang = 'en-US';
      let results = [];

      recognition.onresult = (event) => {
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            results.push(event.results[i][0].transcript);
          }
        }
      };

      recognition.onend = () => {
        if (results.length > 0) {
          this.transcriptions[messageId] = results.join(' ');
        } else {
          this.transcriptions[messageId] = "Could not transcribe audio. Normal mode works best with live speech.";
        }
        this.isTranscribing[messageId] = false;
      };

      recognition.onerror = () => {
        this.isTranscribing[messageId] = false;
        this.transcriptions[messageId] = "Transcription failed.";
      };

      // Start recognition
      recognition.start();
      
      setTimeout(() => {
        if (!this.transcriptions[messageId]) {
           this.transcriptions[messageId] = "Normal transcription is limited. For full accuracy, please use the AI option.";
           this.isTranscribing[messageId] = false;
        }
      }, 3000);
    },

    openTranscribeModal(messageId, audioUrl, isForInput = false) {
      this.transcribeModalData = {
        messageId: isForInput ? 'input' : messageId,
        audioUrl: audioUrl,
        audioBlob: isForInput ? this.selectedVoiceMessage.blob : null,
        isForInput: isForInput
      };
      this.showTranscribeModal = true;
    },

    closeTranscribeModal() {
      this.showTranscribeModal = false;
    },

    async handleTranscriptionChoice(type) {
      this.closeTranscribeModal();
      const { messageId, audioUrl, audioBlob, isForInput } = this.transcribeModalData;
      
      if (type === 'normal') {
        await this.transcribeVoiceMessage(messageId, audioUrl, audioBlob, isForInput);
      } else {
        await this.transcribeAI(messageId, audioUrl, audioBlob, isForInput);
      }
    },

    async transcribeAI(messageId, audioUrl, audioBlob, isForInput) {
      if (this.isTranscribing[messageId]) return;
      this.isTranscribing[messageId] = true;
      
      try {
        // Step 1: Get data (blob or fetch from url)
        let dataToUpload = audioBlob;
        if (!dataToUpload && audioUrl) {
           const response = await fetch(audioUrl);
           dataToUpload = await response.blob();
        }

        if (!dataToUpload) throw new Error("No audio data found");

        // Step 2: Upload to AssemblyAI via Proxy
        const uploadResponse = await api.post('/api/ai/proxy/?path=v2/upload', dataToUpload, {
          headers: {
            'content-type': 'application/octet-stream'
          }
        });

        const uploadUrl = uploadResponse.data.upload_url;

        // Step 3: Request transcription via Proxy
        const transcriptResponse = await api.post('/api/ai/proxy/?path=v2/transcript', {
          audio_url: uploadUrl,
          language_detection: true,
          speech_models: ["universal-3-pro", "universal-2"]
        });

        const transcriptId = transcriptResponse.data.id;

        // Step 4: Polling via Proxy
        let transcript = null;
        let attempts = 0;
        const maxAttempts = 60;

        while (attempts < maxAttempts) {
          const pollingResponse = await api.get(`/api/ai/proxy/?path=v2/transcript/${transcriptId}`);
          
          transcript = pollingResponse.data;
          if (transcript.status === 'completed' || transcript.status === 'error') {
            break;
          }
          attempts++;
          await new Promise(resolve => setTimeout(resolve, 1500));
        }

        if (transcript.status === 'error') {
          throw new Error(transcript.error || "AI Transcription failed");
        }

        if (transcript.status !== 'completed') {
          throw new Error("Transcription timed out");
        }

        const result = transcript.text;

        if (isForInput) {
          this.newMessage += (this.newMessage.length > 0 ? ' ' : '') + result;
        } else {
          this.transcriptions[messageId] = result;
        }
      } catch (error) {
        console.error("AI Transcription Error:", error);
        const errorMsg = error.response?.data?.error || error.message;
        if (isForInput) {
           alert("AI Transcription failed: " + errorMsg);
        } else {
           this.transcriptions[messageId] = "AI Transcription failed: " + errorMsg;
        }
      } finally {
        this.isTranscribing[messageId] = false;
      }
    },

    async processAI(type, targetId, text) {
      if (!text || this.isProcessingAI[targetId]) return;
      this.isProcessingAI[targetId] = true;
      
      try {
        let prompt = "";
        if (type === 'summarize') {
          prompt = `Please provide a very brief, one-sentence summary of the following transcript:\n\n"${text}"`;
        } else if (type === 'rephrase') {
          prompt = `The following is a transcript of a voice message. It might have errors or be informal. Please fix any grammar or spelling errors and rephrase it to be natural and professional, but keep it concise and maintain the original intent:\n\n"${text}"`;
        }

        // Use local Ollama for summarizing and rephrasing
        const response = await api.post('/api/ai/ollama/', {
          prompt: prompt,
          model: 'llama3.2', // Change to 'mistral' or others if preferred
          system: "You are a helpful chat assistant. Handle the transcript as requested. Output ONLY the resulting text. No intros, no conversational fillers."
        });

        const result = response.data.response;

        if (type === 'summarize') {
          this.aiSummaries[targetId] = result;
        } else if (type === 'rephrase') {
          if (targetId === 'input') {
            this.newMessage = result;
          } else {
            this.transcriptions[targetId] = result;
            this.aiSummaries[targetId] = null; // Clear old summary if text changed
          }
        }
      } catch (error) {
        console.error("AI Processing Error:", error);
        const errorDetail = error.response?.data?.error || error.response?.data?.message || error.message;
        alert("AI Processing failed: " + errorDetail);
      } finally {
        this.isProcessingAI[targetId] = false;
      }
    },

    copyToClipboard(text) {
      navigator.clipboard.writeText(text).then(() => {
        // Could add a toast here
      });
    },

    playVoiceMessage(url) {
      const audio = new Audio(url);
      audio.play().catch(error => {
        console.error("Error playing voice message:", error);
      });
    },

    getFileName(url) {
      if (!url) return 'File';
      try {
        const parts = url.split('/');
        const namePart = parts[parts.length - 1];
        // Remove the random suffix Django adds if needed, but usually the last part is fine
        return decodeURIComponent(namePart);
      } catch (e) {
        return 'Download File';
      }
    },

    getFileExt(url) {
      if (!url) return '';
      const parts = url.split('.');
      return parts.length > 1 ? parts.pop().toUpperCase() : 'UNKNOWN';
    },

    deleteMessage(id) {
      if (!confirm("Are you sure you want to delete this message?")) return;
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({
          'action': 'delete',
          'message_id': id,
          'username': this.currentUser
        }));
        // Remove locally immediately for better UX
        this.messages = this.messages.filter(m => m.id !== id);
      }
    },

    startEdit(msg) {
      this.editingMessageId = msg.id;
      this.editingContent = msg.content;
    },

    cancelEdit() {
      this.editingMessageId = null;
      this.editingContent = "";
    },

    async saveEdit() {
      if (!this.editingContent.trim()) return;
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({
          'action': 'edit',
          'message_id': this.editingMessageId,
          'message': this.editingContent,
          'username': this.currentUser
        }));

        // Update locally
        const msg = this.messages.find(m => m.id === this.editingMessageId);
        if (msg) {
          msg.content = this.editingContent;
          msg.is_edited = true;
        }
        
        this.cancelEdit();
      }
    },

    markRoomAsRead() {
      if (this.socket && this.socket.readyState === WebSocket.OPEN && this.roomId) {
        this.socket.send(JSON.stringify({
          'action': 'mark_read',
          'username': this.currentUser
        }));
      }
    },

    scrollToBottom() {
      const el = this.$refs.messageWindow;
      if (el) el.scrollTop = el.scrollHeight;
    },

    formatTime(timestamp) {
      if (!timestamp) return '';
      return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    },

    logout() {
      localStorage.removeItem('access_token');
      localStorage.removeItem('username');
      localStorage.removeItem('last_room_id');
      this.$router.push('/login');
    }
  },

  async mounted() {
    if (!localStorage.getItem('access_token')) {
      this.$router.push('/login');
      return;
    }

    this.initNotificationSocket();

    if (this.roomId) {
      await this.fetchMessages();
      this.initWebSocket();
    }
  },

  beforeUnmount() {
    // Clean up WebSocket
    if (this.socket) this.socket.close();
    
    // Clean up audio playback
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio = null;
    }
    
    // Clean up recording timer
    if (this.recordingTimer) {
      clearInterval(this.recordingTimer);
    }
  }
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
