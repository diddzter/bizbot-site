<?php
/**
 * /tools/ directory index, and /tool-category/<term>/ when a category
 * filter pill is clicked (WP routes both through this template since the
 * taxonomy archive falls back to the post type's archive template).
 */
defined( 'ABSPATH' ) || exit;
get_header();
?>

<section class="bb-section">
	<div class="bb-container">
		<h1>
			<?php
			if ( is_tax( 'tool_category' ) ) {
				single_term_title();
			} else {
				esc_html_e( 'All Tools', 'bizbot' );
			}
			?>
		</h1>

		<div class="bb-category-filters">
			<a href="<?php echo esc_url( home_url( '/tools/' ) ); ?>" class="<?php echo is_post_type_archive( 'tool' ) ? 'is-active' : ''; ?>">
				<?php esc_html_e( 'All', 'bizbot' ); ?>
			</a>
			<?php
			$categories = get_terms( array( 'taxonomy' => 'tool_category', 'hide_empty' => true ) );
			if ( ! is_wp_error( $categories ) ) {
				foreach ( $categories as $cat ) {
					printf(
						'<a href="%s" class="%s">%s</a>',
						esc_url( get_term_link( $cat ) ),
						is_tax( 'tool_category', $cat->slug ) ? 'is-active' : '',
						esc_html( $cat->name )
					);
				}
			}
			?>
		</div>

		<div class="bb-tool-grid">
			<?php
			while ( have_posts() ) :
				the_post();
				$logo = get_field( 'logo_url' );
				$link = get_field( 'outbound_url' );
				$cta  = get_field( 'cta_label' ) ?: __( 'Get it', 'bizbot' );
				$cats = get_the_terms( get_the_ID(), 'tool_category' );
				?>
				<div class="bb-tool-card">
					<?php if ( $logo ) : ?>
						<img class="bb-tool-logo" src="<?php echo esc_url( $logo ); ?>" alt="<?php the_title_attribute(); ?>">
					<?php endif; ?>
					<h3><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h3>
					<p><?php echo esc_html( wp_trim_words( get_the_excerpt(), 22 ) ); ?></p>
					<?php if ( $cats && ! is_wp_error( $cats ) ) : ?>
						<div class="bb-category-tags">
							<?php foreach ( $cats as $cat ) : ?>
								<span><?php echo esc_html( $cat->name ); ?></span>
							<?php endforeach; ?>
						</div>
					<?php endif; ?>
					<?php if ( $link ) : ?>
						<a class="bb-btn bb-btn-outline" href="<?php echo esc_url( $link ); ?>" rel="nofollow sponsored noopener" target="_blank"><?php echo esc_html( $cta ); ?></a>
					<?php endif; ?>
				</div>
			<?php endwhile; ?>
		</div>

		<?php the_posts_pagination(); ?>
	</div>
</section>

<?php get_footer(); ?>
