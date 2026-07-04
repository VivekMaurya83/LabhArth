import './SkeletonCard.css';

/**
 * SkeletonCard — Pulsating placeholder component used during catalog query loads.
 */
export default function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <div className="skeleton-header">
        <div className="skeleton-tags">
          <div className="skeleton-pill skeleton-pill--small shimmer"></div>
          <div className="skeleton-pill skeleton-pill--medium shimmer"></div>
        </div>
        <div className="skeleton-pill skeleton-pill--small shimmer"></div>
      </div>
      
      <div className="skeleton-title shimmer"></div>
      
      <div className="skeleton-meta shimmer"></div>
      
      <div className="skeleton-desc">
        <div className="skeleton-text-line shimmer"></div>
        <div className="skeleton-text-line skeleton-text-line--short shimmer"></div>
      </div>
      
      <div className="skeleton-benefits shimmer"></div>
      
      <div className="skeleton-footer">
        <div className="skeleton-pill skeleton-pill--medium shimmer"></div>
        <div className="skeleton-pill skeleton-pill--small shimmer"></div>
      </div>
    </div>
  );
}
