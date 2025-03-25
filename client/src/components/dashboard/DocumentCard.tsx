'use client';

import Link from 'next/link';

interface Document {
    id: string;
    title: string;
    fileType: string;
    uploadedAt: string;
  }

const DocumentCard = ({ document }: { document: Document }) => {
  return (
    <div>{document.title}</div>
  )
}

export default DocumentCard