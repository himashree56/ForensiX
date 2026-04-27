import { useState, useCallback, useEffect } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import './App.css';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

const API_URL = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [activeTab, setActiveTab] = useState('temporal');
  const [viewMode, setViewMode] = useState('upload');
  const [history, setHistory] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      if (response.ok) {
        setApiStatus('online');
      } else {
        setApiStatus('offline');
      }
    } catch (err) {
      setApiStatus('offline');
    }
  };

  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const response = await fetch(`${API_URL}/history?limit=20`);
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      } else {
        console.error('Failed to fetch history');
      }
    } catch (err) {
      console.error('Error fetching history:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const loadHistoryItem = async (id) => {
    try {
      const response = await fetch(`${API_URL}/history/${id}`);
      if (response.ok) {
        const data = await response.json();
        setResult({
          prediction: data.prediction,
          confidence: data.confidence,
          mean_score: data.mean_score,
          total_frames: data.total_frames,
          fake_frames: data.fake_frames,
          real_frames: data.real_frames,
          uncertain_frames: data.uncertain_frames,
          frame_predictions: data.frame_predictions
        });
        setViewMode('upload'); // Switch to results view
      } else {
        setError('Failed to load analysis details');
      }
    } catch (err) {
      setError('Error loading analysis details');
      console.error('Error:', err);
    }
  };

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && isValidVideoFile(droppedFile)) {
      setFile(droppedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Please upload a valid video file (.mp4, .avi, .mov, .mkv)');
    }
  }, []);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && isValidVideoFile(selectedFile)) {
      setFile(selectedFile);
      setError(null);
      setResult(null);
    } else {
      setError('Please upload a valid video file (.mp4, .avi, .mov, .mkv)');
    }
  };

  const isValidVideoFile = (file) => {
    const validExtensions = ['.mp4', '.avi', '.mov', '.mkv'];
    const fileName = file.name.toLowerCase();
    return validExtensions.some(ext => fileName.endsWith(ext));
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setIsAnalyzing(true);
    setProgress(0);
    setError(null);
    setResult(null);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 500);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('fps', '5');

      const response = await fetch(`${API_URL}/upload-video`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResult(data);
      setProgress(100);
    } catch (err) {
      clearInterval(progressInterval);
      setError(err instanceof Error ? err.message : 'An error occurred during analysis');
      setProgress(0);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setResult(null);
    setError(null);
    setProgress(0);
  };

  const getConfidenceLevel = (confidence) => {
    if (confidence >= 0.8) return 'high';
    if (confidence >= 0.5) return 'medium';
    return 'low';
  };

  // Helper: Calculate Exponential Moving Average (EMA) for smoothing
  const calculateEMA = (scores, alpha = 0.3) => {
    if (scores.length === 0) return [];
    const ema = [scores[0]];
    for (let i = 1; i < scores.length; i++) {
      ema.push(alpha * scores[i] + (1 - alpha) * ema[i - 1]);
    }
    return ema;
  };

  // Helper: Segment frames into windows
  const segmentFrames = (frames, windowSize = 25) => {
    const segments = [];

    for (let i = 0; i < frames.length; i += windowSize) {
      const window = frames.slice(i, Math.min(i + windowSize, frames.length));
      const realCount = window.filter(f => f.prediction === 'REAL').length;
      const fakeCount = window.filter(f => f.prediction === 'FAKE').length;
      const uncertainCount = window.filter(f => f.prediction === 'UNCERTAIN').length;

      segments.push({
        start: i,
        end: Math.min(i + windowSize - 1, frames.length - 1),
        realCount,
        fakeCount,
        uncertainCount,
        totalFrames: window.length,
      });
    }

    return segments;
  };

  // Helper: Calculate confusion matrix (simulated - in real scenario you'd need ground truth)
  const calculateConfusionMatrix = (frames) => {
    const totalFrames = frames.length;
    const predictedFake = frames.filter(f => f.prediction === 'FAKE').length;
    const predictedReal = frames.filter(f => f.prediction === 'REAL').length;
    const predictedUncertain = frames.filter(f => f.prediction === 'UNCERTAIN').length;

    // Simulated metrics (in production, calculate from ground truth)
    return {
      truePositive: Math.round(predictedFake * 0.85), // 85% accuracy assumption
      falsePositive: Math.round(predictedFake * 0.15),
      trueNegative: Math.round(predictedReal * 0.90), // 90% accuracy assumption
      falseNegative: Math.round(predictedReal * 0.10),
      uncertain: predictedUncertain,
      total: totalFrames,
    };
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <div className="logo-icon">🔍</div>
            <div className="logo-text">
              <h1>DeepFake Detector</h1>
              <p>AI-Powered Video Authenticity Analysis</p>
            </div>
          </div>
          <div className="status-badge">
            <div
              className="status-indicator"
              style={{
                background: apiStatus === 'online' ? 'var(--color-success)' : 'var(--color-danger)',
                boxShadow: apiStatus === 'online' ? '0 0 10px var(--color-success)' : '0 0 10px var(--color-danger)'
              }}
            />
            <span>{apiStatus === 'online' ? 'API Online' : apiStatus === 'offline' ? 'API Offline' : 'Checking...'}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main">
        {/* View Mode Toggle */}
        {!result && (
          <div style={{ marginBottom: 'var(--spacing-lg)', textAlign: 'center' }}>
            <div className="view-toggle">
              <button
                className={`toggle-btn ${viewMode === 'upload' ? 'active' : ''}`}
                onClick={() => setViewMode('upload')}
              >
                📤 Upload New Video
              </button>
              <button
                className={`toggle-btn ${viewMode === 'history' ? 'active' : ''}`}
                onClick={() => {
                  setViewMode('history');
                  fetchHistory();
                }}
              >
                📜 View History
              </button>
            </div>
          </div>
        )}

        {/* Upload Section */}
        {!result && viewMode === 'upload' && (
          <div className="upload-section">
            <div className="card">
              <div
                className={`upload-zone ${isDragging ? 'dragging' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-input')?.click()}
              >
                <div className="upload-content">
                  <div className="upload-icon">📹</div>
                  <h3>Upload Video for Analysis</h3>
                  <p>Drag and drop your video here, or click to browse</p>
                  <p style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-tertiary)' }}>
                    Supported formats: MP4, AVI, MOV, MKV (Max 500MB)
                  </p>
                  <input
                    id="file-input"
                    type="file"
                    className="file-input"
                    accept=".mp4,.avi,.mov,.mkv"
                    onChange={handleFileSelect}
                  />
                  <button className="btn btn-primary" style={{ marginTop: 'var(--spacing-md)' }}>
                    Choose File
                  </button>
                </div>
              </div>

              {/* Selected File Display */}
              {file && (
                <div className="selected-file">
                  <div className="file-info">
                    <div className="file-icon">🎬</div>
                    <div className="file-details">
                      <h4>{file.name}</h4>
                      <p>{formatFileSize(file.size)}</p>
                    </div>
                  </div>
                  <button className="remove-btn" onClick={handleReset}>✕</button>
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="error-message">
                  <strong>Error:</strong> {error}
                </div>
              )}

              {/* Analyze Button */}
              {file && !isAnalyzing && (
                <div style={{ marginTop: 'var(--spacing-md)', textAlign: 'center' }}>
                  <button
                    className="btn btn-primary"
                    onClick={handleAnalyze}
                    disabled={apiStatus !== 'online'}
                    style={{ fontSize: 'var(--font-size-lg)', padding: 'var(--spacing-md) var(--spacing-xl)' }}
                  >
                    🚀 Analyze Video
                  </button>
                  {apiStatus !== 'online' && (
                    <p style={{ marginTop: 'var(--spacing-sm)', color: 'var(--color-danger)' }}>
                      API is offline. Please start the backend server.
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* History Section */}
        {!result && viewMode === 'history' && (
          <div className="history-section">
            <div className="card">
              <h2 style={{ marginBottom: 'var(--spacing-lg)' }}>📜 Analysis History</h2>

              {loadingHistory && (
                <div style={{ textAlign: 'center', padding: 'var(--spacing-xl)' }}>
                  <div className="spinner"></div>
                  <p style={{ marginTop: 'var(--spacing-md)', color: 'var(--color-text-secondary)' }}>
                    Loading history...
                  </p>
                </div>
              )}

              {!loadingHistory && history.length === 0 && (
                <div style={{ textAlign: 'center', padding: 'var(--spacing-xl)' }}>
                  <div style={{ fontSize: '4rem', marginBottom: 'var(--spacing-md)' }}>📭</div>
                  <h3>No Analysis History</h3>
                  <p style={{ color: 'var(--color-text-secondary)', marginTop: 'var(--spacing-sm)' }}>
                    Upload and analyze a video to see it here
                  </p>
                </div>
              )}

              {!loadingHistory && history.length > 0 && (
                <div className="history-grid">
                  {history.map((item) => (
                    <div
                      key={item.id}
                      className="history-card"
                      onClick={() => loadHistoryItem(item.id)}
                    >
                      <div className="history-header">
                        <div className="history-filename">
                          <span className="file-icon">🎬</span>
                          <span className="filename-text">{item.filename}</span>
                        </div>
                        <div className={`prediction-badge ${item.prediction.toLowerCase()}`}>
                          {item.prediction}
                        </div>
                      </div>

                      <div className="history-stats">
                        <div className="stat-item">
                          <span className="stat-label">Confidence</span>
                          <span className="stat-value">{(item.confidence * 100).toFixed(1)}%</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Frames</span>
                          <span className="stat-value">{item.total_frames}</span>
                        </div>
                        <div className="stat-item">
                          <span className="stat-label">Size</span>
                          <span className="stat-value">
                            {(item.file_size / (1024 * 1024)).toFixed(1)} MB
                          </span>
                        </div>
                      </div>

                      <div className="history-footer">
                        <span className="history-date">
                          {new Date(item.upload_timestamp).toLocaleString()}
                        </span>
                        {item.processing_time && (
                          <span className="processing-time">
                            ⏱️ {item.processing_time.toFixed(1)}s
                          </span>
                        )}
                      </div>

                      <div className="history-breakdown">
                        <div className="breakdown-bar">
                          <div
                            className="breakdown-segment real"
                            style={{ width: `${(item.real_frames / item.total_frames) * 100}%` }}
                            title={`Real: ${item.real_frames} frames`}
                          />
                          <div
                            className="breakdown-segment uncertain"
                            style={{ width: `${(item.uncertain_frames / item.total_frames) * 100}%` }}
                            title={`Uncertain: ${item.uncertain_frames} frames`}
                          />
                          <div
                            className="breakdown-segment fake"
                            style={{ width: `${(item.fake_frames / item.total_frames) * 100}%` }}
                            title={`Fake: ${item.fake_frames} frames`}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Progress Section */}
        {isAnalyzing && (
          <div className="progress-section">
            <div className="card">
              <div className="progress-header">
                <h3>Analyzing Video...</h3>
                <span className="progress-percentage">{progress}%</span>
              </div>
              <div className="progress-bar-container">
                <div className="progress-bar" style={{ width: `${progress}%` }} />
              </div>
              <div className="progress-status">
                <p>
                  {progress < 30 && '📤 Uploading video...'}
                  {progress >= 30 && progress < 60 && '🎞️ Extracting frames...'}
                  {progress >= 60 && progress < 90 && '🔍 Analyzing frames with AI...'}
                  {progress >= 90 && '📊 Generating results...'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="results-section">
            <div className="card">
              <div className="result-header">
                <h2>Analysis Complete</h2>
                <div
                  className={`prediction-badge ${result.prediction.toLowerCase()}`}
                >
                  {result.prediction === 'DEEPFAKE' && '⚠️ DEEPFAKE DETECTED'}
                  {result.prediction === 'REAL' && '✅ AUTHENTIC VIDEO'}
                  {result.prediction === 'UNCERTAIN' && '❓ UNCERTAIN'}
                </div>
              </div>

              {/* Confidence Display */}
              <div className="confidence-display">
                <div className="confidence-label">
                  <h3>Confidence Score</h3>
                  <span className="confidence-value">
                    {(result.confidence * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="confidence-bar-container">
                  <div
                    className={`confidence-bar ${getConfidenceLevel(result.confidence)}`}
                    style={{ width: `${result.confidence * 100}%` }}
                  />
                </div>
              </div>

              {/* Stats Grid */}
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-label">Total Frames</div>
                  <div className="stat-value">{result.total_frames}</div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Fake Frames</div>
                  <div className="stat-value" style={{ color: 'var(--color-danger)' }}>
                    {result.fake_frames}
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Real Frames</div>
                  <div className="stat-value" style={{ color: 'var(--color-success)' }}>
                    {result.real_frames}
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Mean Score</div>
                  <div className="stat-value">{result.mean_score.toFixed(3)}</div>
                </div>
              </div>

              {/* Frame Timeline - Forensic Analysis Visualizations */}
              <div className="frame-timeline">
                <h3>🔬 Forensic Frame-by-Frame Analysis</h3>

                {/* Tab Selection */}
                <div className="chart-tabs">
                  <button
                    className={`tab-btn ${activeTab === 'temporal' ? 'active' : ''}`}
                    onClick={() => setActiveTab('temporal')}
                  >
                    📈 Temporal Analysis
                  </button>
                  <button
                    className={`tab-btn ${activeTab === 'segmented' ? 'active' : ''}`}
                    onClick={() => setActiveTab('segmented')}
                  >
                    📊 Segment Summary
                  </button>
                  <button
                    className={`tab-btn ${activeTab === 'confusion' ? 'active' : ''}`}
                    onClick={() => setActiveTab('confusion')}
                  >
                    🎯 Model Validation
                  </button>
                  <button
                    className={`tab-btn ${activeTab === 'list' ? 'active' : ''}`}
                    onClick={() => setActiveTab('list')}
                  >
                    📋 Detailed List
                  </button>
                </div>

                {/* 1. TEMPORAL LINE CHART - Primary Evidence Chart */}
                {activeTab === 'temporal' && (() => {
                  const scores = result.frame_predictions.map(f => f.score);
                  const smoothedScores = calculateEMA(scores, 0.3);

                  return (
                    <div className="chart-container">
                      <div className="chart-description">
                        <p><strong>Purpose:</strong> Temporal deepfake behavior analysis showing persistence vs noise</p>
                        <p><strong>Legend:</strong> Raw score (thin line), Smoothed score (thick line), Shaded zones indicate classification regions</p>
                      </div>
                      <Line
                        data={{
                          labels: result.frame_predictions.map((_, i) => `${i}`),
                          datasets: [
                            {
                              label: 'Fake Zone (0.65-1.0)',
                              data: Array(result.frame_predictions.length).fill(1),
                              backgroundColor: 'rgba(239, 68, 68, 0.1)',
                              borderColor: 'transparent',
                              fill: {
                                target: { value: 0.65 },
                                above: 'rgba(239, 68, 68, 0.1)',
                              },
                              pointRadius: 0,
                              order: 3,
                            },
                            {
                              label: 'Uncertain Zone (0.35-0.65)',
                              data: Array(result.frame_predictions.length).fill(0.65),
                              backgroundColor: 'rgba(234, 179, 8, 0.1)',
                              borderColor: 'transparent',
                              fill: {
                                target: { value: 0.35 },
                                above: 'rgba(234, 179, 8, 0.1)',
                              },
                              pointRadius: 0,
                              order: 3,
                            },
                            {
                              label: 'Real Zone (0-0.35)',
                              data: Array(result.frame_predictions.length).fill(0.35),
                              backgroundColor: 'rgba(34, 197, 94, 0.1)',
                              borderColor: 'transparent',
                              fill: {
                                target: { value: 0 },
                                above: 'rgba(34, 197, 94, 0.1)',
                              },
                              pointRadius: 0,
                              order: 3,
                            },
                            {
                              label: 'Smoothed Score (EMA)',
                              data: smoothedScores,
                              borderColor: 'rgb(138, 92, 246)',
                              backgroundColor: 'rgba(138, 92, 246, 0.2)',
                              borderWidth: 3,
                              fill: false,
                              tension: 0.4,
                              pointRadius: 0,
                              pointHoverRadius: 6,
                              order: 1,
                            },
                            {
                              label: 'Raw Score',
                              data: scores,
                              borderColor: 'rgba(138, 92, 246, 0.5)',
                              backgroundColor: 'transparent',
                              borderWidth: 1,
                              fill: false,
                              tension: 0,
                              pointRadius: 0,
                              pointHoverRadius: 4,
                              order: 2,
                            },
                            {
                              label: 'Fake Threshold (0.65)',
                              data: Array(result.frame_predictions.length).fill(0.65),
                              borderColor: 'rgba(239, 68, 68, 0.8)',
                              borderWidth: 2,
                              borderDash: [10, 5],
                              fill: false,
                              pointRadius: 0,
                              order: 0,
                            },
                            {
                              label: 'Real Threshold (0.35)',
                              data: Array(result.frame_predictions.length).fill(0.35),
                              borderColor: 'rgba(34, 197, 94, 0.8)',
                              borderWidth: 2,
                              borderDash: [10, 5],
                              fill: false,
                              pointRadius: 0,
                              order: 0,
                            },
                          ],
                        }}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          interaction: {
                            mode: 'index',
                            intersect: false,
                          },
                          plugins: {
                            legend: {
                              display: true,
                              position: 'top',
                              labels: {
                                color: 'rgb(229, 229, 229)',
                                font: { size: 11 },
                                padding: 10,
                                usePointStyle: true,
                              },
                            },
                            tooltip: {
                              backgroundColor: 'rgba(0, 0, 0, 0.9)',
                              titleColor: '#fff',
                              bodyColor: '#fff',
                              borderColor: 'rgb(138, 92, 246)',
                              borderWidth: 1,
                              padding: 12,
                              displayColors: true,
                              callbacks: {
                                title: function (context) {
                                  const idx = context[0].dataIndex;
                                  const frame = result.frame_predictions[idx];
                                  return `Frame ${frame.frame_number} (${frame.timestamp.toFixed(2)}s)`;
                                },
                                label: function (context) {
                                  if (context.datasetIndex === 3) {
                                    return `Smoothed: ${context.parsed.y?.toFixed(4) || 'N/A'}`;
                                  } else if (context.datasetIndex === 4) {
                                    const frame = result.frame_predictions[context.dataIndex];
                                    return `Raw: ${context.parsed.y?.toFixed(4) || 'N/A'} (${frame.prediction})`;
                                  }
                                  return '';
                                }
                              }
                            },
                          },
                          scales: {
                            x: {
                              title: {
                                display: true,
                                text: 'Frame Number',
                                color: 'rgb(229, 229, 229)',
                                font: { size: 13, weight: 'bold' },
                              },
                              ticks: {
                                color: 'rgb(163, 163, 163)',
                                maxTicksLimit: 20,
                              },
                              grid: {
                                color: 'rgba(255, 255, 255, 0.05)',
                              },
                            },
                            y: {
                              min: 0,
                              max: 1,
                              title: {
                                display: true,
                                text: 'Deepfake Probability (0 = Real, 1 = Fake)',
                                color: 'rgb(229, 229, 229)',
                                font: { size: 13, weight: 'bold' },
                              },
                              ticks: {
                                color: 'rgb(163, 163, 163)',
                                callback: function (value) {
                                  return typeof value === 'number' ? value.toFixed(2) : value;
                                }
                              },
                              grid: {
                                color: 'rgba(255, 255, 255, 0.1)',
                              },
                            },
                          },
                        }}
                      />
                    </div>
                  );
                })()}

                {/* 2. SEGMENTED STACKED BAR CHART - High-level Summary */}
                {activeTab === 'segmented' && (() => {
                  const segments = segmentFrames(result.frame_predictions, 25);

                  return (
                    <div className="chart-container">
                      <div className="chart-description">
                        <p><strong>Purpose:</strong> Identify suspicious segments of the video at a glance</p>
                        <p><strong>Each bar:</strong> Represents 25 frames showing % Real, % Uncertain, % Fake</p>
                      </div>
                      <Bar
                        data={{
                          labels: segments.map(s => `${s.start}-${s.end}`),
                          datasets: [
                            {
                              label: '% Real',
                              data: segments.map(s => (s.realCount / s.totalFrames) * 100),
                              backgroundColor: 'rgba(34, 197, 94, 0.8)',
                              borderColor: 'rgb(34, 197, 94)',
                              borderWidth: 1,
                            },
                            {
                              label: '% Uncertain',
                              data: segments.map(s => (s.uncertainCount / s.totalFrames) * 100),
                              backgroundColor: 'rgba(234, 179, 8, 0.8)',
                              borderColor: 'rgb(234, 179, 8)',
                              borderWidth: 1,
                            },
                            {
                              label: '% Fake',
                              data: segments.map(s => (s.fakeCount / s.totalFrames) * 100),
                              backgroundColor: 'rgba(239, 68, 68, 0.8)',
                              borderColor: 'rgb(239, 68, 68)',
                              borderWidth: 1,
                            },
                          ],
                        }}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: {
                              display: true,
                              position: 'top',
                              labels: {
                                color: 'rgb(229, 229, 229)',
                                font: { size: 12 },
                                padding: 15,
                              },
                            },
                            tooltip: {
                              backgroundColor: 'rgba(0, 0, 0, 0.9)',
                              titleColor: '#fff',
                              bodyColor: '#fff',
                              borderColor: 'rgb(138, 92, 246)',
                              borderWidth: 1,
                              padding: 12,
                              callbacks: {
                                title: function (context) {
                                  const seg = segments[context[0].dataIndex];
                                  return `Frames ${seg.start}-${seg.end} (${seg.totalFrames} frames)`;
                                },
                                label: function (context) {
                                  return `${context.dataset.label}: ${context.parsed.y?.toFixed(1) || 'N/A'}%`;
                                },
                                footer: function (context) {
                                  const seg = segments[context[0].dataIndex];
                                  return `Real: ${seg.realCount} | Uncertain: ${seg.uncertainCount} | Fake: ${seg.fakeCount}`;
                                }
                              }
                            },
                          },
                          scales: {
                            x: {
                              stacked: true,
                              title: {
                                display: true,
                                text: 'Frame Segments',
                                color: 'rgb(229, 229, 229)',
                                font: { size: 13, weight: 'bold' },
                              },
                              ticks: {
                                color: 'rgb(163, 163, 163)',
                                maxRotation: 45,
                                minRotation: 45,
                              },
                              grid: {
                                display: false,
                              },
                            },
                            y: {
                              stacked: true,
                              min: 0,
                              max: 100,
                              title: {
                                display: true,
                                text: 'Percentage (%)',
                                color: 'rgb(229, 229, 229)',
                                font: { size: 13, weight: 'bold' },
                              },
                              ticks: {
                                color: 'rgb(163, 163, 163)',
                                callback: function (value) {
                                  return typeof value === 'number' ? value.toFixed(0) + '%' : value;
                                }
                              },
                              grid: {
                                color: 'rgba(255, 255, 255, 0.1)',
                              },
                            },
                          },
                        }}
                      />
                    </div>
                  );
                })()}

                {/* 3. CONFUSION MATRIX HEATMAP - Model Validation */}
                {activeTab === 'confusion' && (() => {
                  const matrix = calculateConfusionMatrix(result.frame_predictions);
                  const precision = matrix.truePositive / (matrix.truePositive + matrix.falsePositive) || 0;
                  const recall = matrix.truePositive / (matrix.truePositive + matrix.falseNegative) || 0;
                  const f1Score = 2 * (precision * recall) / (precision + recall) || 0;

                  return (
                    <div className="chart-container confusion-matrix-container">
                      <div className="chart-description">
                        <p><strong>Purpose:</strong> Model trust and credibility assessment</p>
                        <p><strong>Note:</strong> Simulated metrics for demonstration (requires ground truth for real validation)</p>
                      </div>

                      <div className="confusion-matrix">
                        <div className="matrix-grid">
                          <div className="matrix-label-top">
                            <div></div>
                            <div className="matrix-header">Predicted Real</div>
                            <div className="matrix-header">Predicted Fake</div>
                          </div>

                          <div className="matrix-row">
                            <div className="matrix-header">Actual Real</div>
                            <div className="matrix-cell true-negative">
                              <div className="cell-value">{matrix.trueNegative}</div>
                              <div className="cell-label">True Negative</div>
                            </div>
                            <div className="matrix-cell false-positive">
                              <div className="cell-value">{matrix.falsePositive}</div>
                              <div className="cell-label">False Positive</div>
                            </div>
                          </div>

                          <div className="matrix-row">
                            <div className="matrix-header">Actual Fake</div>
                            <div className="matrix-cell false-negative">
                              <div className="cell-value">{matrix.falseNegative}</div>
                              <div className="cell-label">False Negative</div>
                            </div>
                            <div className="matrix-cell true-positive">
                              <div className="cell-value">{matrix.truePositive}</div>
                              <div className="cell-label">True Positive</div>
                            </div>
                          </div>
                        </div>

                        <div className="metrics-panel">
                          <h4>📊 Performance Metrics</h4>
                          <div className="metric-item">
                            <span className="metric-label">Precision:</span>
                            <span className="metric-value">{(precision * 100).toFixed(1)}%</span>
                            <div className="metric-bar">
                              <div className="metric-fill" style={{ width: `${precision * 100}%` }}></div>
                            </div>
                          </div>
                          <div className="metric-item">
                            <span className="metric-label">Recall:</span>
                            <span className="metric-value">{(recall * 100).toFixed(1)}%</span>
                            <div className="metric-bar">
                              <div className="metric-fill" style={{ width: `${recall * 100}%` }}></div>
                            </div>
                          </div>
                          <div className="metric-item">
                            <span className="metric-label">F1 Score:</span>
                            <span className="metric-value">{(f1Score * 100).toFixed(1)}%</span>
                            <div className="metric-bar">
                              <div className="metric-fill" style={{ width: `${f1Score * 100}%` }}></div>
                            </div>
                          </div>
                          <div className="metric-item">
                            <span className="metric-label">Total Frames:</span>
                            <span className="metric-value">{matrix.total}</span>
                          </div>
                          <div className="metric-item">
                            <span className="metric-label">Uncertain:</span>
                            <span className="metric-value">{matrix.uncertain}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })()}

                {/* 4. LIST VIEW - Detailed Frame Information */}
                {activeTab === 'list' && (
                  <div className="timeline-container">
                    {result.frame_predictions.map((frame) => (
                      <div key={frame.frame_number} className="frame-item">
                        <span className="frame-number">
                          Frame {frame.frame_number}
                        </span>
                        <div className="frame-bar-container">
                          <div
                            className={`frame-bar ${frame.prediction.toLowerCase()}`}
                            style={{ width: `${frame.score * 100}%` }}
                          />
                        </div>
                        <span className="frame-score">{frame.score.toFixed(3)}</span>
                        <span className={`frame-label ${frame.prediction.toLowerCase()}`}>
                          {frame.prediction}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Reset Button */}
              <div style={{ marginTop: 'var(--spacing-xl)', textAlign: 'center' }}>
                <button className="btn btn-primary" onClick={handleReset}>
                  🔄 Analyze Another Video
                </button>
              </div>
            </div>
          </div>
        )
        }
      </main >
    </div >
  );
}

export default App;
