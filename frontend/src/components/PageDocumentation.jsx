import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

import { DOCS_DATA } from '../data/wiki';

export default function PageDocumentation({ activeDoc: externalActiveDoc, setActiveDoc: externalSetActiveDoc }) {
    const [localActiveDoc, setLocalActiveDoc] = useState('intro');
    const activeDoc = externalActiveDoc || localActiveDoc;
    const setActiveDoc = externalSetActiveDoc || setLocalActiveDoc;

    return (
        <div style={{ display: 'flex', height: '100%', border: '1px solid #333', borderRadius: 8, overflow: 'hidden' }}>
            {/* Sidebar */}
            <div style={{ width: 320, background: 'rgba(0,0,0,0.4)', borderRight: '1px solid #333', overflowY: 'auto', padding: 16 }}>
                <h3 style={{ marginTop: 0, color: '#a78bfa', fontSize: 16 }}>Theory Wiki</h3>

                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    <li style={{ marginBottom: 8 }}>
                        <div
                            style={{ padding: '8px 12px', borderRadius: 4, cursor: 'pointer', background: activeDoc === 'intro' ? 'rgba(167, 139, 250, 0.2)' : 'transparent', color: activeDoc === 'intro' ? '#a78bfa' : '#ccc' }}
                            onClick={() => setActiveDoc('intro')}
                        >
                            📄 {DOCS_DATA['intro'].title}
                        </div>
                    </li>

                    <li style={{ marginBottom: 8 }}>
                        <div style={{ padding: '8px 12px', color: '#888', fontWeight: 'bold' }}>🧠 Lý thuyết Điều khiển</div>
                        <ul style={{ listStyle: 'none', paddingLeft: 20, margin: 0 }}>
                            <li style={{ marginTop: 4 }}>
                                <div
                                    style={{ padding: '6px 12px', borderRadius: 4, cursor: 'pointer', fontSize: 13, background: activeDoc === 'control_philosophies' ? 'rgba(167, 139, 250, 0.2)' : 'transparent', color: activeDoc === 'control_philosophies' ? '#a78bfa' : '#ccc' }}
                                    onClick={() => setActiveDoc('control_philosophies')}
                                >{DOCS_DATA['control_philosophies'].title}</div>
                            </li>
                            <li style={{ marginTop: 4 }}>
                                <div
                                    style={{ padding: '6px 12px', borderRadius: 4, cursor: 'pointer', fontSize: 13, background: activeDoc === 'modeling' ? 'rgba(167, 139, 250, 0.2)' : 'transparent', color: activeDoc === 'modeling' ? '#a78bfa' : '#ccc' }}
                                    onClick={() => setActiveDoc('modeling')}
                                >{DOCS_DATA['modeling'].title}</div>
                            </li>
                            <li style={{ marginTop: 4 }}>
                                <div
                                    style={{ padding: '6px 12px', borderRadius: 4, cursor: 'pointer', fontSize: 13, background: activeDoc === 'integrators' ? 'rgba(167, 139, 250, 0.2)' : 'transparent', color: activeDoc === 'integrators' ? '#a78bfa' : '#ccc' }}
                                    onClick={() => setActiveDoc('integrators')}
                                >{DOCS_DATA['integrators'].title}</div>
                            </li>
                        </ul>
                    </li>

                    <li style={{ marginBottom: 8 }}>
                        <div style={{ padding: '8px 12px', color: '#888', fontWeight: 'bold' }}>⚡ Tối ưu & Vận hành</div>
                        <ul style={{ listStyle: 'none', paddingLeft: 20, margin: 0 }}>
                            <li style={{ marginTop: 4 }}>
                                <div
                                    style={{ padding: '6px 12px', borderRadius: 4, cursor: 'pointer', fontSize: 13, background: activeDoc === 'auto_tuning' ? 'rgba(167, 139, 250, 0.2)' : 'transparent', color: activeDoc === 'auto_tuning' ? '#a78bfa' : '#ccc' }}
                                    onClick={() => setActiveDoc('auto_tuning')}
                                >{DOCS_DATA['auto_tuning'].title}</div>
                            </li>
                            <li style={{ marginTop: 4 }}>
                                <div
                                    style={{ padding: '6px 12px', borderRadius: 4, cursor: 'pointer', fontSize: 13, background: activeDoc === 'gain_scheduling' ? 'rgba(167, 139, 250, 0.2)' : 'transparent', color: activeDoc === 'gain_scheduling' ? '#a78bfa' : '#ccc' }}
                                    onClick={() => setActiveDoc('gain_scheduling')}
                                >{DOCS_DATA['gain_scheduling'].title}</div>
                            </li>
                            <li style={{ marginTop: 4 }}>
                                <div
                                    style={{ padding: '6px 12px', borderRadius: 4, cursor: 'pointer', fontSize: 13, background: activeDoc === 'objective_func' ? 'rgba(167, 139, 250, 0.2)' : 'transparent', color: activeDoc === 'objective_func' ? '#a78bfa' : '#ccc' }}
                                    onClick={() => setActiveDoc('objective_func')}
                                >{DOCS_DATA['objective_func'].title}</div>
                            </li>
                        </ul>
                    </li>

                    <li style={{ marginBottom: 8 }}>
                        <div style={{ padding: '8px 12px', color: '#888', fontWeight: 'bold' }}>⚠️ Phân tích Rủi ro</div>
                        <ul style={{ listStyle: 'none', paddingLeft: 20, margin: 0 }}>
                            <li style={{ marginTop: 4 }}>
                                <div
                                    style={{ padding: '6px 12px', borderRadius: 4, cursor: 'pointer', fontSize: 13, background: activeDoc === 'limitations' ? 'rgba(167, 139, 250, 0.2)' : 'transparent', color: activeDoc === 'limitations' ? '#a78bfa' : '#ccc' }}
                                    onClick={() => setActiveDoc('limitations')}
                                >{DOCS_DATA['limitations'].title}</div>
                            </li>
                        </ul>
                    </li>
                </ul>
            </div>

            {/* Content Area */}
            <div style={{ flex: 1, padding: '24px 40px', overflowY: 'auto', background: 'rgba(0,0,0,0.2)' }}>
                <div className="markdown-body" style={{ color: '#ddd', fontSize: 15, lineHeight: 1.6 }}>
                    <ReactMarkdown
                        remarkPlugins={[remarkMath]}
                        rehypePlugins={[rehypeKatex]}
                        components={{
                            h1: ({ node, ...props }) => <h1 style={{ color: '#a78bfa', borderBottom: '1px solid #333', paddingBottom: 10 }} {...props} />,
                            h2: ({ node, ...props }) => <h2 style={{ color: '#fff', marginTop: 30 }} {...props} />,
                            h3: ({ node, ...props }) => <h3 style={{ color: '#e2e8f0', marginTop: 25 }} {...props} />,
                            strong: ({ node, ...props }) => <strong style={{ color: '#f59e0b' }} {...props} />,
                            blockquote: ({ node, ...props }) => <blockquote style={{ borderLeft: '4px solid #f59e0b', margin: '20px 0', padding: '10px 20px', backgroundColor: 'rgba(245, 158, 11, 0.1)' }} {...props} />,
                        }}
                    >
                        {DOCS_DATA[activeDoc]?.content || 'Nội dung đang được cập nhật...'}
                    </ReactMarkdown>
                </div>
            </div>
        </div>
    );
}
