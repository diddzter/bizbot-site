<?php
/**
 * Site header. Deliberately does not include GeneratePress's default header
 * markup -- BizBot's header is a simple logo + 3-link nav + CTA, no promo
 * bar (the old Unicorn Platform promo bar was a builder-injected ad, not
 * real site content, and is intentionally not carried over).
 */
defined( 'ABSPATH' ) || exit;
?>
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
	<meta charset="<?php bloginfo( 'charset' ); ?>">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="bb-header">
	<div class="bb-container bb-header-inner" style="display:flex;align-items:center;justify-content:space-between;padding:20px 0;">
		<a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="bb-logo" style="font-weight:700;font-size:1.2rem;text-decoration:none;color:var(--bb-ink);">
			BB <span style="font-weight:400;color:var(--bb-muted);">Business Admin Tools</span>
		</a>
		<nav class="bb-nav" aria-label="<?php esc_attr_e( 'Primary', 'bizbot' ); ?>">
			<?php
			wp_nav_menu(
				array(
					'theme_location' => 'primary',
					'container'      => false,
					'fallback_cb'    => 'bizbot_default_menu_fallback',
				)
			);
			?>
		</nav>
		<a class="bb-btn" href="<?php echo esc_url( home_url( '/#submit-tool' ) ); ?>">
			<?php esc_html_e( 'Submit your tool!', 'bizbot' ); ?>
		</a>
	</div>
</header>

<?php
function bizbot_default_menu_fallback() {
	echo '<ul style="display:flex;gap:20px;list-style:none;margin:0;padding:0;">';
	echo '<li><a href="' . esc_url( home_url( '/' ) ) . '">Home</a></li>';
	$about = get_page_by_path( 'about-us' );
	if ( $about ) {
		echo '<li><a href="' . esc_url( get_permalink( $about ) ) . '">About Us</a></li>';
	}
	echo '<li><a href="' . esc_url( get_permalink( get_page_by_path( 'blog' ) ) ?: home_url( '/blog/' ) ) . '">Blog</a></li>';
	echo '</ul>';
}
