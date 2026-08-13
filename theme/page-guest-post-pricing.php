<?php
/**
 * Matched automatically by WP's template hierarchy for the page whose slug
 * is "guest-post-pricing". Pricing tiers mirror data/pages_seed.json's
 * "guest-post-pricing" entry.
 */
defined( 'ABSPATH' ) || exit;
get_header();

$tiers = array(
	array( 'plan' => 'Basic', 'articles' => 6, 'price' => '$150/year' ),
	array( 'plan' => 'Standard', 'articles' => 16, 'price' => '$250/year' ),
	array( 'plan' => 'Premium', 'articles' => 25, 'price' => '$350/year' ),
);
?>

<section class="bb-section bb-container" style="max-width:820px;">
	<h1 style="text-align:center;"><?php esc_html_e( 'Guest Post Pricing', 'bizbot' ); ?></h1>
	<p class="bb-section-lead" style="text-align:center;margin:0 auto;">
		<?php esc_html_e( 'Boost your online presence with high-quality guest posts.', 'bizbot' ); ?>
	</p>
	<blockquote style="text-align:center;color:var(--bb-muted);font-style:italic;margin:24px auto;max-width:600px;">
		&ldquo;<?php esc_html_e( 'Backlinks remain one of the most important factors for SEO success, helping websites improve visibility and authority.', 'bizbot' ); ?>&rdquo; &mdash; Moz
	</blockquote>

	<div class="bb-pricing-grid">
		<?php foreach ( $tiers as $tier ) : ?>
			<div class="bb-pricing-card">
				<h3><?php echo esc_html( $tier['plan'] ); ?></h3>
				<div class="bb-price"><?php echo esc_html( $tier['price'] ); ?></div>
				<p><?php echo esc_html( $tier['articles'] ); ?> <?php esc_html_e( 'articles', 'bizbot' ); ?></p>
				<p><?php esc_html_e( '2 do-follow backlinks', 'bizbot' ); ?></p>
				<p style="color:var(--bb-muted);font-size:0.85rem;"><?php esc_html_e( 'Cancel anytime, Premium support', 'bizbot' ); ?></p>
			</div>
		<?php endforeach; ?>
	</div>

	<p style="color:var(--bb-muted);font-size:0.9rem;">
		<?php esc_html_e( 'Link insertions are offered at the same price. Pricing is based on client-provided articles. If we prepare the content, an additional $25 per article applies. After one year of publishing your article, we can add additional links to that article.', 'bizbot' ); ?>
	</p>

	<h2><?php esc_html_e( 'Our Publishing Network', 'bizbot' ); ?></h2>
	<ul>
		<li><a href="https://www.bizbot.com/">bizbot.com</a></li>
		<li><a href="https://www.sales-leads-crm.com/">sales-leads-crm.com</a></li>
		<li><a href="https://www.content-and-marketing.com/">content-and-marketing.com</a></li>
		<li><a href="https://work-smart-not-hard.tech/">work-smart-not-hard.tech</a></li>
	</ul>

	<div class="bb-section bb-section--soft" style="text-align:center;border-radius:var(--bb-radius);">
		<h2><?php esc_html_e( 'Ready to Grow Your Online Presence?', 'bizbot' ); ?></h2>
		<p>
			<?php esc_html_e( 'Select the package that fits your goals or contact us for a custom solution. With Bizbot.com, you\'ll get more than guest posts — you\'ll get a partner committed to your SEO success.', 'bizbot' ); ?>
		</p>
		<p>📧 <a href="mailto:didrik@bizbot.no">didrik@bizbot.no</a></p>
		<?php bizbot_render_form( 'bizbot_guest_post_contact_shortcode', __( 'Guest post contact', 'bizbot' ) ); ?>
	</div>
</section>

<?php get_footer(); ?>
