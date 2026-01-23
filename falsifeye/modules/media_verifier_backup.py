import os
import cv2
import numpy as np
import librosa
from PIL import Image, ImageChops
from scipy.fftpack import fft2, fftshift

def analyze_media(filepath, media_type):
    """
    Analyzes media for potential tampering using advanced Signal Processing & ML.
    Returns a dictionary with 'score' (0-100, higher is more likely fake) and 'details'.
    """
    if media_type == 'image':
        return analyze_image(filepath)
    elif media_type == 'video':
        return analyze_video(filepath)
    elif media_type == 'audio':
        return analyze_audio(filepath)
    elif media_type == 'document':
        return analyze_document(filepath)
    else:
        return {'score': 0, 'details': 'Unknown media type'}

def analyze_image(filepath):
    try:
        original = Image.open(filepath).convert('RGB')
        
        # 1. ELA (Error Level Analysis)
        # Re-save at 90% quality and check difference.
        # High difference in specific regions (like faces) vs background indicates manipulation.
        temp_path = filepath + ".ela.jpg"
        original.save(temp_path, 'JPEG', quality=90)
        resaved = Image.open(temp_path)
        
        ela_image = ImageChops.difference(original, resaved)
        extrema = ela_image.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        os.remove(temp_path)

        # 2. Frequency Domain Analysis (FFT)
        # Deepfakes often leave artifacts in the high-frequency domain
        img_gray = original.convert('L')
        f = fft2(img_gray)
        fshift = fftshift(f)
        magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)
        avg_freq_energy = np.mean(magnitude_spectrum)

        score = 0
        details = []
        
        # ELA Scoring
        if max_diff > 60: # Stricter threshold
            score += 40
            details.append(f"High ELA difference ({max_diff}) indicates potential splicing/editing.")
        else:
            details.append(f"ELA levels normal ({max_diff}).")

        # FFT Scoring
        if avg_freq_energy > 160:
            score += 30
            details.append("Abnormal frequency spectrum detected (potential GAN artifacts).")
        
        return {
            'score': min(100, max(10, score)),
            'details': " ".join(details)
        }
    except Exception as e:
        return {'score': 0, 'details': f'Error analyzing image: {str(e)}'}

def analyze_video(filepath):
    try:
        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            return {'score': 0, 'details': 'Could not open video file.'}

        # Load Haar Cascades
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

        frame_count = 0
        analyzed_frames = 0
        
        # Metrics
        blur_scores = []
        fft_scores = []
        optical_flow_scores = []
        
        prev_gray = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            # Analyze every 3rd frame
            if frame_count % 3 == 0:
                analyzed_frames += 1
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 1. Blur Check
                variance = cv2.Laplacian(gray, cv2.CV_64F).var()
                blur_scores.append(variance)

                # 2. Optical Flow (Motion Consistency)
                if prev_gray is not None:
                    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                    optical_flow_scores.append(np.mean(mag))
                prev_gray = gray

                # 3. Face Analysis
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                for (x,y,w,h) in faces:
                    # FFT on Face ROI
                    face_roi = gray[y:y+h, x:x+w]
                    f = fft2(face_roi)
                    fshift = fftshift(f)
                    magnitude = 20 * np.log(np.abs(fshift) + 1)
                    fft_scores.append(np.mean(magnitude))

        cap.release()
        
        if analyzed_frames == 0:
            return {'score': 0, 'details': 'Video processed but no frames analyzed.'}

        # Analysis Logic
        avg_blur = np.mean(blur_scores) if blur_scores else 0
        avg_fft = np.mean(fft_scores) if fft_scores else 0
        avg_flow = np.mean(optical_flow_scores) if optical_flow_scores else 0
        
        score = 0
        details = []
        
        details.append(f"Analyzed {analyzed_frames} frames.")
        
        # Blur Scoring
        if avg_blur < 100:
            score += 20
            details.append("Video is consistently blurry (hides artifacts).")
        
        # FFT Scoring (GAN Artifacts)
        if avg_fft > 160:
            score += 35
            details.append("High-frequency artifacts detected in face region (GAN signature).")

        # Optical Flow Scoring
        # Deepfakes often have "jittery" faces or unnatural stillness
        if avg_flow < 0.5:
            score += 20
            details.append("Unnatural lack of micro-movements (potential static mask).")
        elif avg_flow > 10:
            score += 20
            details.append("Excessive unnatural motion artifacts.")

        return {
            'score': min(100, max(10, score)),
            'details': " ".join(details)
        }
    except Exception as e:
        return {'score': 0, 'details': f'Error analyzing video: {str(e)}'}

def analyze_audio(filepath):
    try:
        # Load audio
        y, sr = librosa.load(filepath, duration=30)
        
        # 1. Extract MFCCs (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        mfcc_var = np.var(mfccs, axis=1)
        
        # 2. Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(y)
        zcr_mean = np.mean(zcr)

        # 3. Spectral Rolloff (High frequency content)
        rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        rolloff_mean = np.mean(rolloff)
        
        score = 0
        details = []
        
        # Check for "Flatness" / Robotic nature
        avg_mfcc_var = np.mean(mfcc_var)
        details.append(f"Voice Variance: {avg_mfcc_var:.2f}.")
        
        if avg_mfcc_var < 200: 
            score += 40
            details.append("Low voice variance detected (potential synthesis).")
        
        # High frequency cut-offs common in cheap TTS
        if rolloff_mean < 3000:
            score += 20
            details.append("Low spectral bandwidth (potential low-quality TTS).")

        return {
            'score': min(100, max(10, score)),
            'details': " ".join(details)
        }
    except Exception as e:
        return {'score': 0, 'details': f'Error analyzing audio: {str(e)}'}

def analyze_document(filepath):
    try:
        import PyPDF2
        score = 0
        details = []
        
        if filepath.lower().endswith('.pdf'):
            try:
                with open(filepath, 'rb') as f:
                    pdf = PyPDF2.PdfReader(f)
                    info = pdf.metadata
                    
                    if info:
                        producer = info.get('/Producer', '')
                        creator = info.get('/Creator', '')
                        
                        details.append(f"Producer: {producer}, Creator: {creator}")
                        
                        suspicious_tools = ['photoshop', 'gimp', 'ilovepdf', 'editor', 'phantompdf']
                        if any(tool in producer.lower() for tool in suspicious_tools) or \
                           any(tool in creator.lower() for tool in suspicious_tools):
                            score += 60
                            details.append("Metadata indicates use of editing software.")
                        else:
                            details.append("Metadata appears consistent with standard generation.")
                            
                        # Check for JavaScript (sometimes used in malicious PDFs)
                        # This is a basic check
                        try:
                            for page in pdf.pages:
                                if '/JS' in page or '/JavaScript' in page:
                                    score += 30
                                    details.append("JavaScript detected in PDF (potential security risk/dynamic content).")
                                    break
                        except:
                            pass
                    else:
                        score += 20
                        details.append("No metadata found (potentially stripped).")
            except Exception as e:
                return {'score': 0, 'details': f'Error reading PDF: {str(e)}'}
        else:
             details.append("Basic text/image document analysis not fully implemented.")

        return {
            'score': min(100, max(10, score)),
            'details': " | ".join(details)
        }
    except ImportError:
        return {'score': 0, 'details': 'PyPDF2 not installed. Cannot analyze documents.'}
    except Exception as e:
        return {'score': 0, 'details': f'Error analyzing document: {str(e)}'}
