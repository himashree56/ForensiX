# Deepfake Detection Frontend

Modern React + TypeScript frontend for deepfake video detection.

## Features

- ✨ Beautiful dark-themed UI with premium aesthetics
- 📤 Drag-and-drop video upload
- 📊 Real-time progress tracking
- 🎯 Comprehensive results visualization
- 📈 Frame-by-frame analysis timeline
- 🎨 Smooth animations and micro-interactions
- 📱 Fully responsive design

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **CSS Variables** for theming
- **Google Fonts (Inter)** for typography

## Installation

```bash
# Install dependencies
npm install
```

## Development

```bash
# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

## Building for Production

```bash
# Build production bundle
npm run build

# Preview production build
npm run preview
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── src/
│   ├── App.tsx          # Main application component
│   ├── App.css          # Component styles (empty - using index.css)
│   ├── index.css        # Global styles and design system
│   └── main.tsx         # Application entry point
├── public/              # Static assets
├── .env                 # Environment variables
├── vite.config.ts       # Vite configuration
└── package.json         # Dependencies
```

## API Integration

The frontend communicates with the FastAPI backend through:

- **Health Check**: `GET /health` - Check API status
- **Video Upload**: `POST /upload-video` - Upload and analyze video

## Design System

### Color Palette

- **Primary**: Purple gradient (`hsl(260, 85%, 60%)`)
- **Success**: Green (`hsl(142, 71%, 45%)`)
- **Danger**: Red (`hsl(0, 84%, 60%)`)
- **Background**: Dark theme with subtle gradients

### Typography

- **Font**: Inter (Google Fonts)
- **Sizes**: Responsive scale from 0.75rem to 2.5rem

### Components

- **Card**: Container with glassmorphism effect
- **Button**: Primary and secondary variants with hover effects
- **Progress Bar**: Animated with shimmer effect
- **Upload Zone**: Drag-and-drop with visual feedback
- **Results Display**: Comprehensive analysis visualization

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Performance

- Code splitting with Vite
- Lazy loading of components
- Optimized animations with CSS transforms
- Efficient re-renders with React hooks
