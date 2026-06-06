import {
  Component, OnInit, OnDestroy, ViewChild, ElementRef,
  ChangeDetectorRef, NgZone, AfterViewChecked, ViewEncapsulation
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { AuthService } from '../auth/auth.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isNew?: boolean;
}

@Component({
  selector: 'app-chatbot',
  standalone: true,
  encapsulation: ViewEncapsulation.None,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './chatbot.component.html',
  styleUrls: ['./chatbot.component.scss']
})
export class ChatbotComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesEnd') messagesEnd!: ElementRef;
  @ViewChild('inputRef') inputRef!: ElementRef;

  isOpen: boolean = false;
  isTyping: boolean = false;
  inputText: string = '';
  messages: ChatMessage[] = [];
  userId: string = 'user_001'; // set in ngOnInit
  shouldScroll: boolean = false;

  private apiUrl = environment.apiUrl;

  quickQuestions = [
    '🤒 I have fever and headache',
    '🩸 How to stop bleeding?',
    '🔥 First aid for burns',
    '💊 Medicines after surgery',
    '🥗 Diet for fast recovery',
    '🚨 When to call ambulance?',
  ];

  constructor(
    private http: HttpClient,
    private auth: AuthService,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit(): void {
    this.userId = this.auth.userId;
    // Listen for open event from dashboard
    window.addEventListener('open-medibot', () => {
      this.ngZone.run(() => { this.isOpen = true; this.shouldScroll = true; this.cdr.detectChanges(); });
    });
    // Welcome message
    this.messages.push({
      role: 'assistant',
      content: "Hi! 👋 I'm **MediBot**, your MediConnect health assistant.\n\nI can help with first aid, recovery tips, diet advice, and more. What do you need help with today?",
      timestamp: new Date()
    });
  }

  ngAfterViewChecked(): void {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  toggleChat(): void {
    this.isOpen = !this.isOpen;
    if (this.isOpen) {
      this.shouldScroll = true;
      setTimeout(() => this.inputRef?.nativeElement?.focus(), 300);
    }
  }

  closeChat(): void {
    this.isOpen = false;
  }

  sendMessage(text?: string): void {
    const msg = (text || this.inputText).trim();
    if (!msg || this.isTyping) return;

    // Add user message
    this.messages.push({ role: 'user', content: msg, timestamp: new Date(), isNew: true });
    this.inputText = '';
    this.isTyping = true;
    this.shouldScroll = true;
    this.cdr.detectChanges();

    // Build history (exclude welcome message)
    const history = this.messages
      .filter(m => !m.isNew)
      .slice(-10)
      .map(m => ({ role: m.role, content: m.content }));

    this.http.post<{ reply: string }>(`${this.apiUrl}/api/chatbot/message`, {
      user_id: this.userId,
      message: msg,
      history
    }).subscribe({
      next: (res) => {
        this.ngZone.run(() => {
          this.isTyping = false;
          this.messages.push({
            role: 'assistant',
            content: res.reply,
            timestamp: new Date(),
            isNew: true
          });
          // Clear isNew after animation
          setTimeout(() => {
            this.messages.forEach(m => m.isNew = false);
          }, 600);
          this.shouldScroll = true;
          this.cdr.detectChanges();
        });
      },
      error: () => {
        this.ngZone.run(() => {
          this.isTyping = false;
          this.messages.push({
            role: 'assistant',
            content: "Sorry, I'm having trouble connecting. For emergencies please call **108** immediately. 🚨",
            timestamp: new Date()
          });
          this.shouldScroll = true;
          this.cdr.detectChanges();
        });
      }
    });
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  clearChat(): void {
    this.messages = [{
      role: 'assistant',
      content: "Hi! 👋 I'm **MediBot**. How can I help you today?",
      timestamp: new Date()
    }];
  }

  scrollToBottom(): void {
    try {
      this.messagesEnd?.nativeElement?.scrollIntoView({ behavior: 'smooth' });
    } catch {}
  }

  // Format markdown bold (**text**) and newlines
  formatMessage(content: string): string {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
  }

  getTime(date: Date): string {
    return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
  }
}